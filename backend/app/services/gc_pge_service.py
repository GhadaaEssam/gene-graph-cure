from fastapi import UploadFile # Assuming loguru based on your logger usage, adjust if standard logging
import torch
import pandas as pd
import io
import numpy as np
from pathlib import Path
import sys
from typing import Dict, List, Optional, Union
from scipy.special import erfinv
import logging

logger = logging.getLogger(__name__)

# --- Module path setup ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "gcpge"))

import model
sys.modules["model.model"] = model  

from gcpge.preprocess import preprocess_for_inference

class GC_PGE_Service:
    MULTIOMICS_FILE_KEYS = ("meth_features", "cnv_features", "snv_features")
    EPSILON = np.finfo(float).eps

    # --- MODIFIED: Expects a dictionary of base models and one multiomics model ---
    def __init__(self, model_paths: Dict[str, str], multiomics_model_path: Optional[str] = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # 1. Load the Base Model Zoo
        self.base_models = {}
        for c_type, path in model_paths.items():
            if Path(path).exists():
                self.base_models[c_type] = self._load_model(path)
                logger.info(f"Loaded Base Model: {c_type}")
            else:
                logger.warning(f"Warning: Missing Base Model for {c_type} at {path}")

        # 2. Load the Single Master Multiomics Model (Removed list/ensemble logic)
        self.multiomics_model = None
        if multiomics_model_path and Path(multiomics_model_path).exists():
            self.multiomics_model = self._load_model(multiomics_model_path)
            logger.info(f"Loaded Master Multi-omics Model from: {multiomics_model_path}")

    def _load_model(self, model_path: str):
        loaded_model = torch.load(
            model_path,
            map_location=self.device,
            weights_only=False
        )
        loaded_model.to(self.device)
        loaded_model.eval()
        return loaded_model

    def _supports_multiomics(self, loaded_model) -> bool:
        return all(
            hasattr(loaded_model, attr)
            for attr in ("enc_meth", "enc_cnv", "enc_snv", "fusion", "final_classifier")
        )

    async def predict_from_files(self, raw_files: Dict[str, Union[UploadFile, str]], include_graph: bool = True):
        # 1. Safely extract the cancer type (works whether it arrives as string or bytes)
        raw_cancer_val = raw_files.pop("cancer_type", "breast")
        if isinstance(raw_cancer_val, bytes):
            raw_cancer_type = raw_cancer_val.decode("utf-8").lower()
        elif hasattr(raw_cancer_val, 'read'): # In case FastAPI sends it as a file object
            raw_cancer_type = (await raw_cancer_val.read()).decode("utf-8").lower()
        else:
            raw_cancer_type = str(raw_cancer_val).lower()
        
        # Normalize cancer string
        if "melanin" in raw_cancer_type or "immunotherapy" in raw_cancer_type:
            cancer_type = "immunotherapy"
        elif "liver" in raw_cancer_type:
            cancer_type = "liver"
        elif "ovarian" in raw_cancer_type:
            cancer_type = "ovarian"
        else:
            cancer_type = "breast"

        # 2. Read the omics files from the streams
        contents = {
            key: await f.read()
            for key, f in raw_files.items()
            if hasattr(f, 'read')
        }
        
        contents["cancer_type"] = cancer_type
        
        has_multiomics = any(key in contents for key in self.MULTIOMICS_FILE_KEYS)
        has_all_multiomics = all(key in contents for key in self.MULTIOMICS_FILE_KEYS)
        
        if has_multiomics and not has_all_multiomics:
            missing = [key for key in self.MULTIOMICS_FILE_KEYS if key not in contents]
            raise ValueError(
                "Multi-omics prediction requires all three optional files: "
                + ", ".join(missing)
            )
            
        use_multiomics = False
        if cancer_type == "breast" and has_all_multiomics:
            use_multiomics = True
            logger.info("Multi-omics files detected for breast cancer. Routing to Master Multi-Omics Model.")
        else:
            logger.info(f"Route: {cancer_type.upper()} CANCER -> SINGLE-OMICS BASE MODEL")

        # --- MODIFIED: Inject Internal Server Networks based on routing ---
        folder_name = "breast_multiomics" if use_multiomics else cancer_type
        network_dir = PROJECT_ROOT / "model_inputs" / folder_name
        
        if not network_dir.exists():
            raise ValueError(f"Internal network data folder not found for: {folder_name}")

        # We load them as bytes so your existing _build_base_input logic works natively!
        with open(network_dir / "anchor_genes.csv", "rb") as f: contents["anchor_genes"] = f.read()
        with open(network_dir / "node_features.csv", "rb") as f: contents["node_features"] = f.read()
        with open(network_dir / "ppi_edges.csv", "rb") as f: contents["ppi_edges"] = f.read()
        with open(network_dir / "homolog_edges.csv", "rb") as f: contents["homolog_edges"] = f.read()

        # 3. Build Inputs
        processed_data = self._build_base_input(contents)
        processed_data["cancer_type"] = cancer_type # Save this so predict_base knows which model to use

        if use_multiomics:
            processed_data["omics"] = self._build_multiomics_input(contents)

        return self.predict(processed_data, include_graph=include_graph)

    # -------------------------------------------------------------
    # Helper parsing functions remain EXACTLY as you wrote them!
    # -------------------------------------------------------------
    def _build_base_input(self, contents: Dict[str, bytes]) -> dict:
        processed_data = {}
        data_sample = pd.read_csv(io.BytesIO(contents["geo_features"]), header=None)
        processed_data["geo_features"] = data_sample.iloc[:, 1:] 
        processed_data["anchor_genes"] = pd.read_csv(io.BytesIO(contents["anchor_genes"]), header=0)
        data_x_raw = pd.read_csv(io.BytesIO(contents["node_features"]), header=0)
        processed_data["node_features"] = data_x_raw.iloc[:, 1:]
        processed_data["ppi_edges"] = pd.read_csv(io.BytesIO(contents["ppi_edges"]), header=0)
        processed_data["homolog_edges"] = pd.read_csv(io.BytesIO(contents["homolog_edges"]), header=0)
        return processed_data

    def _read_omics_frame(self, contents: Dict[str, bytes], key: str) -> pd.DataFrame:
        frame = pd.read_csv(io.BytesIO(contents[key]), header=0)
        if frame.shape[1] < 2: raise ValueError(f"{key} must contain a sample-id column and at least one gene column")
        frame = frame.set_index(frame.columns[0])
        frame.index = frame.index.map(str)
        frame.columns = frame.columns.map(str)
        frame = frame.loc[~frame.index.duplicated(keep="first")]
        frame = frame.loc[:, ~frame.columns.duplicated(keep="first")]
        frame = frame.apply(pd.to_numeric, errors="coerce")
        if frame.isnull().values.any(): raise ValueError(f"{key} contains non-numeric omics values")
        return frame

    def _rank_gauss_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        max_value = frame.values.max()
        if abs(max_value) < self.EPSILON: max_value = self.EPSILON
        rank_gauss = (frame.values / max_value - 0.5) * 2
        rank_gauss = np.clip(rank_gauss, -1 + self.EPSILON, 1 - self.EPSILON)
        rank_gauss = erfinv(rank_gauss)
        return pd.DataFrame(rank_gauss, columns=frame.columns, index=frame.index)

    def _build_multiomics_input(self, contents: Dict[str, bytes]) -> Dict[str, Union[pd.DataFrame, List[str]]]:
        omics_frames = {
            "data_geo_x": self._read_omics_frame(contents, "geo_features"),
            "data_meth_x": self._read_omics_frame(contents, "meth_features"),
            "data_cnv_x": self._read_omics_frame(contents, "cnv_features"),
            "data_snv_x": self._read_omics_frame(contents, "snv_features"),
        }
        node_features_raw = pd.read_csv(io.BytesIO(contents["node_features"]), header=0)
        node_count = node_features_raw.shape[0]
        node_gene_ids = node_features_raw.iloc[:, 0].astype(str).tolist()

        rna_frame = omics_frames["data_geo_x"]
        shared_samples = set.intersection(*(set(frame.index) for frame in omics_frames.values()))
        shared_genes = set.intersection(*(set(frame.columns) for frame in omics_frames.values()))
        aligned_samples = [sample_id for sample_id in rna_frame.index if sample_id in shared_samples]
        aligned_genes = [gene_id for gene_id in node_gene_ids if gene_id in shared_genes]
        
        if not aligned_genes: aligned_genes = [gene_id for gene_id in rna_frame.columns if gene_id in shared_genes]
        if not aligned_samples: raise ValueError("No shared samples were found across the uploaded omics matrices")
        if not aligned_genes: raise ValueError("No shared genes were found across the uploaded omics matrices")
        if len(aligned_genes) != node_count: raise ValueError(f"Aligned omics gene count does not match the node feature count ({len(aligned_genes)} != {node_count})")

        aligned_omics = {}
        for name, frame in omics_frames.items():
            aligned_omics[name] = self._rank_gauss_frame(frame.loc[aligned_samples, aligned_genes])

        aligned_omics["sample_ids"] = aligned_samples
        aligned_omics["gene_ids"] = aligned_genes
        return aligned_omics

    def predict(self, raw_input: dict, include_graph: bool = True):
        if "omics" in raw_input:
            return self.predict_multiomics(raw_input, include_graph=include_graph)
        return self.predict_base(raw_input, include_graph=include_graph)

    # --- MODIFIED: Added Cancer-Type routing to the correct base model ---
    def predict_base(self, raw_input: dict, include_graph: bool = True):
        cancer_type = raw_input.get("cancer_type", "breast")
        target_model = self.base_models.get(cancer_type)
        
        if not target_model:
            raise ValueError(f"Base model weights not loaded for cancer type: {cancer_type}")

        with torch.no_grad():
            data, geo_tensor = preprocess_for_inference(raw_input)
            data = data.to(self.device)
            geo_tensor = geo_tensor.to(self.device)

            result = target_model(data, geo_tensor)
            
            # Add final prediction labels
            if "out" in result:
                result["prediction"] = result["out"].argmax(dim=1)

            json_serializable_result = self._to_json_serializable(result)
            return self._filter_heavy_outputs(json_serializable_result, include_graph=include_graph)

    # --- MODIFIED: Removed the loop; strictly uses the single master model ---
    def predict_multiomics(self, raw_input: dict, include_graph: bool = True):
        if not self.multiomics_model:
            raise ValueError("Multi-omics files were provided, but the master multi-omics checkpoint is missing.")

        with torch.no_grad():
            data, _ = preprocess_for_inference(raw_input)
            data = data.to(self.device)

            omics = raw_input["omics"]
            x_rna = torch.tensor(omics["data_geo_x"].values, dtype=torch.float).to(self.device)
            x_meth = torch.tensor(omics["data_meth_x"].values, dtype=torch.float).to(self.device)
            x_cnv = torch.tensor(omics["data_cnv_x"].values, dtype=torch.float).to(self.device)
            x_snv = torch.tensor(omics["data_snv_x"].values, dtype=torch.float).to(self.device)

            result = self.multiomics_model(
                data,
                x_rna,
                x_meth=x_meth,
                x_cnv=x_cnv,
                x_snv=x_snv
            )

            if "out_multiomics" not in result:
                raise RuntimeError("Multi-omics model did not return 'out_multiomics'")

            probabilities = torch.exp(result["out_multiomics"])
            result["out_multiomics_probabilities"] = probabilities
            result["prediction"] = probabilities.argmax(dim=1)
            result["sample_ids"] = omics["sample_ids"]
            result["gene_ids"] = omics["gene_ids"]

            return self._filter_heavy_outputs(
                self._to_json_serializable(result),
                include_graph=include_graph
            )

    def _to_json_serializable(self, result: dict):
        json_serializable_result = {}
        for key, value in result.items():
            if isinstance(value, torch.Tensor):
                json_serializable_result[key] = value.detach().cpu().tolist()
            elif isinstance(value, (np.ndarray, np.generic)):
                json_serializable_result[key] = value.tolist()
            else:
                json_serializable_result[key] = value
        return json_serializable_result

    def _filter_heavy_outputs(self, result: dict, include_graph: bool):
        if include_graph or "graph" not in result:
            return result

        graph = result.pop("graph")
        if isinstance(graph, list):
            rows = len(graph)
            cols = len(graph[0]) if rows and isinstance(graph[0], list) else 0
            result["graph_shape"] = [rows, cols]
        else:
            result["graph_shape"] = None

        return result
    