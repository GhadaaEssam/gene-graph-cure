import torch
import pandas as pd
import io
import numpy as np
from pathlib import Path
import sys
from typing import Dict, List, Optional, Union
from scipy.special import erfinv

# --- Module path setup ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "gcpge"))

import model
sys.modules["model.model"] = model  

from gcpge.preprocess import preprocess_for_inference

class GC_PGE_Service:
    MULTIOMICS_FILE_KEYS = ("meth_features", "cnv_features", "snv_features")
    EPSILON = np.finfo(float).eps

    def __init__(self, model_path: str, multiomics_model_paths: Optional[List[str]] = None):

        # Validate model path at initialization
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model weights not found at: {model_path}")

        # Set device (GPU if available, else CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load base model once
        self.model = self._load_model(model_path)

        self.multiomics_models = []
        for path in multiomics_model_paths or []:
            if path:
                self.multiomics_models.append(self._load_model(path))

        # If the main model is a multi-omics checkpoint, allow it to serve both
        # RNA-only and late-fusion requests.
        if not self.multiomics_models and self._supports_multiomics(self.model):
            self.multiomics_models = [self.model]

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

    async def predict_from_files(self, files_dict: dict, include_graph: bool = True):
        """
        Mirrors the original research model's data handling logic.
        If methylation, CNV, and SNV files are present, the request is routed
        through the multi-omics late-fusion branch. Otherwise it stays on the
        original RNA-only path.
        """
        # 1. Read the files from the streams
        contents = {
            key: await f.read()
            for key, f in files_dict.items()
            if f is not None
        }

        has_multiomics = any(key in contents for key in self.MULTIOMICS_FILE_KEYS)
        has_all_multiomics = all(key in contents for key in self.MULTIOMICS_FILE_KEYS)
        if has_multiomics and not has_all_multiomics:
            missing = [key for key in self.MULTIOMICS_FILE_KEYS if key not in contents]
            raise ValueError(
                "Multi-omics prediction requires all three optional files: "
                + ", ".join(missing)
            )

        processed_data = self._build_base_input(contents)

        if has_all_multiomics:
            processed_data["omics"] = self._build_multiomics_input(contents)

        # 2. Call the prediction logic with the correctly sliced DataFrames
        return self.predict(processed_data, include_graph=include_graph)

    def _build_base_input(self, contents: Dict[str, bytes]) -> dict:
        processed_data = {}

        # Sample expression matrix: First col is name, rest is data
        data_sample = pd.read_csv(io.BytesIO(contents["geo_features"]), header=0)
        processed_data["geo_features"] = data_sample.iloc[:, 1:] 

        # Characteristic genes (Anchor list)
        processed_data["anchor_genes"] = pd.read_csv(io.BytesIO(contents["anchor_genes"]), header=0)

        # Signal path network (data_x): First col is ID, rest is data
        data_x_raw = pd.read_csv(io.BytesIO(contents["node_features"]), header=0)
        processed_data["node_features"] = data_x_raw.iloc[:, 1:]

        # PPI network
        processed_data["ppi_edges"] = pd.read_csv(io.BytesIO(contents["ppi_edges"]), header=0)

        # Same origin network (Homolog)
        processed_data["homolog_edges"] = pd.read_csv(io.BytesIO(contents["homolog_edges"]), header=0)

        return processed_data

    def _read_omics_frame(self, contents: Dict[str, bytes], key: str) -> pd.DataFrame:
        frame = pd.read_csv(io.BytesIO(contents[key]), header=0)
        if frame.shape[1] < 2:
            raise ValueError(f"{key} must contain a sample-id column and at least one gene column")

        frame = frame.set_index(frame.columns[0])
        frame.index = frame.index.map(str)
        frame.columns = frame.columns.map(str)
        frame = frame.loc[~frame.index.duplicated(keep="first")]
        frame = frame.loc[:, ~frame.columns.duplicated(keep="first")]
        frame = frame.apply(pd.to_numeric, errors="coerce")

        if frame.isnull().values.any():
            raise ValueError(f"{key} contains non-numeric omics values")

        return frame

    def _rank_gauss_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        max_value = frame.values.max()
        if abs(max_value) < self.EPSILON:
            max_value = self.EPSILON

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
        if not aligned_genes:
            aligned_genes = [gene_id for gene_id in rna_frame.columns if gene_id in shared_genes]

        if not aligned_samples:
            raise ValueError("No shared samples were found across the uploaded omics matrices")
        if not aligned_genes:
            raise ValueError("No shared genes were found across the uploaded omics matrices")
        if len(aligned_genes) != node_count:
            raise ValueError(
                "Aligned omics gene count does not match the node feature count "
                f"({len(aligned_genes)} != {node_count})"
            )

        aligned_omics = {}
        for name, frame in omics_frames.items():
            aligned_omics[name] = self._rank_gauss_frame(frame.loc[aligned_samples, aligned_genes])

        aligned_omics["sample_ids"] = aligned_samples
        aligned_omics["gene_ids"] = aligned_genes
        return aligned_omics

    def predict(self, raw_input: dict, include_graph: bool = True):
        """
        Runs inference and returns all output keys from the selected model path
        as JSON-serializable lists.
        """
        if "omics" in raw_input:
            return self.predict_multiomics(raw_input, include_graph=include_graph)

        return self.predict_base(raw_input, include_graph=include_graph)

    def predict_base(self, raw_input: dict, include_graph: bool = True):
        """
        Runs the original RNA-only/base GC-PGE inference path.
        """
        with torch.no_grad():
            # 1. Preprocess data
            data, geo_tensor = preprocess_for_inference(raw_input)

            # 2. Move to device
            data = data.to(self.device)
            geo_tensor = geo_tensor.to(self.device)

            # 3. Forward pass
            # 'result' is the dictionary returned by your model's forward method
            result = self.model(data, geo_tensor)

            # 4. Clean up and convert ALL keys automatically
            json_serializable_result = {}
            for key, value in result.items():
                if isinstance(value, torch.Tensor):
                    # Detach, move to CPU, and convert to nested list
                    json_serializable_result[key] = value.detach().cpu().tolist()
                elif isinstance(value, (np.ndarray, np.generic)):
                    # Handle any numpy arrays that might be in the output
                    json_serializable_result[key] = value.tolist()
                else:
                    # Keep native Python types (ints, floats, lists) as is
                    json_serializable_result[key] = value

            return self._filter_heavy_outputs(
                json_serializable_result,
                include_graph=include_graph
            )

    def predict_multiomics(self, raw_input: dict, include_graph: bool = True):
        """
        Runs late-fusion inference for RNA, methylation, CNV, and SNV inputs.
        Multiple configured checkpoints are averaged as a soft-voting ensemble.
        """
        if not self.multiomics_models:
            raise ValueError(
                "Multi-omics files were provided, but no multi-omics checkpoint is configured"
            )

        with torch.no_grad():
            data, _ = preprocess_for_inference(raw_input)
            data = data.to(self.device)

            omics = raw_input["omics"]
            x_rna = torch.tensor(omics["data_geo_x"].values, dtype=torch.float).to(self.device)
            x_meth = torch.tensor(omics["data_meth_x"].values, dtype=torch.float).to(self.device)
            x_cnv = torch.tensor(omics["data_cnv_x"].values, dtype=torch.float).to(self.device)
            x_snv = torch.tensor(omics["data_snv_x"].values, dtype=torch.float).to(self.device)

            accumulated = {}
            log_probability_keys = {"out", "out_multiomics", "temp"}

            for loaded_model in self.multiomics_models:
                if not self._supports_multiomics(loaded_model):
                    raise ValueError(
                        "Configured multi-omics checkpoint does not include the late-fusion branch"
                    )

                result = loaded_model(
                    data,
                    x_rna,
                    x_meth=x_meth,
                    x_cnv=x_cnv,
                    x_snv=x_snv
                )

                if "out_multiomics" not in result:
                    raise RuntimeError("Multi-omics model did not return 'out_multiomics'")

                for key, value in result.items():
                    if not isinstance(value, torch.Tensor):
                        continue

                    value_to_add = torch.exp(value) if key in log_probability_keys else value
                    accumulated[key] = accumulated.get(key, 0) + value_to_add

            model_count = len(self.multiomics_models)
            averaged = {}
            for key, value in accumulated.items():
                averaged_value = value / model_count
                if key in log_probability_keys:
                    averaged_value = torch.log(averaged_value.clamp_min(self.EPSILON))
                averaged[key] = averaged_value

            probabilities = torch.exp(averaged["out_multiomics"])
            averaged["out_multiomics_probabilities"] = probabilities
            averaged["prediction"] = probabilities.argmax(dim=1)
            averaged["sample_ids"] = omics["sample_ids"]
            averaged["gene_ids"] = omics["gene_ids"]

            return self._filter_heavy_outputs(
                self._to_json_serializable(averaged),
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
