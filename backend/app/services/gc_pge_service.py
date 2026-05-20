import io
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
import torch
from fastapi import UploadFile
from scipy.special import erfinv

# --- Module path setup ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "gcpge"))

import model

sys.modules["model.model"] = model

from gcpge.preprocess import preprocess_for_inference

logger = logging.getLogger(__name__)


class GC_PGE_Service:
    CORE_RESULT_LIMIT = 10
    MULTIOMICS_FILE_KEYS = ("meth_features", "cnv_features", "snv_features")
    STATIC_INPUT_FILENAMES = {
        "anchor_genes": "anchor_genes.csv",
        "node_features": "node_features.csv",
        "ppi_edges": "ppi_edges.csv",
        "homolog_edges": "homolog_edges.csv",
    }
    EPSILON = np.finfo(float).eps

    def __init__(
        self,
        model_paths: Union[Dict[str, str], str],
        multiomics_model_path: Optional[str] = None,
    ):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.pathway_id_labels = self._load_pathway_id_labels(
            PROJECT_ROOT / "gcpge" / "pw_id.csv"
        )

        self.base_models = {}
        self.base_model_paths = {}
        if isinstance(model_paths, (str, Path)):
            self.base_model_paths["default"] = str(model_paths)
        else:
            for cancer_type, path in model_paths.items():
                self.base_model_paths[cancer_type] = path

        self.multiomics_model = None
        self.multiomics_model_path = multiomics_model_path

    def _load_model(self, model_path: str):
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model weights not found at: {model_path}")

        loaded_model = torch.load(
            model_path,
            map_location=self.device,
            weights_only=False,
        )
        loaded_model.to(self.device)
        loaded_model.eval()
        return loaded_model

    def _supports_multiomics(self, loaded_model) -> bool:
        return all(
            hasattr(loaded_model, attr)
            for attr in ("enc_meth", "enc_cnv", "enc_snv", "fusion", "final_classifier")
        )

    def _get_base_model(self, cancer_type: str):
        model_key = cancer_type if cancer_type in self.base_model_paths else "default"
        if model_key not in self.base_model_paths:
            raise ValueError(f"Base model weights not configured for cancer type: {cancer_type}")

        if model_key not in self.base_models:
            self.base_models[model_key] = self._load_model(self.base_model_paths[model_key])
            logger.info("Loaded base model: %s", model_key)

        return self.base_models[model_key]

    def _get_multiomics_model(self):
        if self.multiomics_model is None:
            if not self.multiomics_model_path:
                raise ValueError("Multi-omics model path is not configured.")

            self.multiomics_model = self._load_model(self.multiomics_model_path)
            logger.info("Loaded master multi-omics model from: %s", self.multiomics_model_path)

        return self.multiomics_model

    async def predict_from_geo_file(
        self,
        geo_features: UploadFile,
        static_inputs_dir: Path,
        cancer_type: str = "default",
        include_graph: bool = True,
    ):
        """
        Runs base-model prediction with patient GEO features and static model
        inputs stored on disk for the selected model.
        """
        self._validate_static_inputs(static_inputs_dir)

        contents = {
            "cancer_type": cancer_type,
            "geo_features": await geo_features.read(),
        }
        for key, filename in self.STATIC_INPUT_FILENAMES.items():
            with open(static_inputs_dir / filename, "rb") as f:
                contents[key] = f.read()

        processed_data = self._build_base_input(contents)
        processed_data["cancer_type"] = cancer_type
        return self.predict(processed_data, include_graph=include_graph)

    async def predict_from_files(
        self,
        raw_files: Dict[str, Union[UploadFile, str]],
        include_graph: bool = True,
    ):
        raw_files = dict(raw_files)
        cancer_type = await self._normalize_cancer_type(raw_files.pop("cancer_type", "breast"))

        contents = {
            key: await f.read()
            for key, f in raw_files.items()
            if f is not None and hasattr(f, "read")
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

        use_multiomics = cancer_type == "breast" and has_all_multiomics
        folder_name = "breast_multiomics" if use_multiomics else cancer_type
        network_dir = PROJECT_ROOT / "model_inputs" / folder_name
        self._validate_static_inputs(network_dir)

        for key, filename in self.STATIC_INPUT_FILENAMES.items():
            with open(network_dir / filename, "rb") as f:
                contents[key] = f.read()

        processed_data = self._build_base_input(contents)
        processed_data["cancer_type"] = cancer_type

        if use_multiomics:
            processed_data["omics"] = self._build_multiomics_input(contents)
            logger.info("Routing breast request to multi-omics model.")
        else:
            logger.info("Routing %s request to base RNA model.", cancer_type)

        return self.predict(processed_data, include_graph=include_graph)

    async def _normalize_cancer_type(self, raw_cancer_value) -> str:
        if isinstance(raw_cancer_value, bytes):
            raw_cancer_type = raw_cancer_value.decode("utf-8").lower()
        elif hasattr(raw_cancer_value, "read"):
            raw_cancer_type = (await raw_cancer_value.read()).decode("utf-8").lower()
        else:
            raw_cancer_type = str(raw_cancer_value).lower()

        if "melanin" in raw_cancer_type or "immunotherapy" in raw_cancer_type:
            return "immunotherapy"
        if "liver" in raw_cancer_type:
            return "liver"
        if "ovarian" in raw_cancer_type:
            return "ovarian"
        return "breast"

    @classmethod
    def _validate_static_inputs(cls, static_inputs_dir: Path) -> None:
        missing_files = [
            filename
            for filename in cls.STATIC_INPUT_FILENAMES.values()
            if not (static_inputs_dir / filename).exists()
        ]
        if missing_files:
            raise FileNotFoundError(
                f"Missing static model input files in {static_inputs_dir}: "
                f"{', '.join(missing_files)}"
            )

    def _build_base_input(self, contents: Dict[str, bytes]) -> dict:
        data_sample = pd.read_csv(io.BytesIO(contents["geo_features"]), header=0)
        anchor_genes = pd.read_csv(io.BytesIO(contents["anchor_genes"]), header=0)
        data_x_raw = pd.read_csv(io.BytesIO(contents["node_features"]), header=0)

        processed_data = {
            "geo_features": data_sample.iloc[:, 1:],
            "anchor_genes": anchor_genes,
            "node_features": data_x_raw.iloc[:, 1:],
            "ppi_edges": pd.read_csv(io.BytesIO(contents["ppi_edges"]), header=0),
            "homolog_edges": pd.read_csv(io.BytesIO(contents["homolog_edges"]), header=0),
        }

        anchor_gene_names = self._extract_gene_names(anchor_genes)
        processed_data["_anchor_gene_names"] = anchor_gene_names
        processed_data["_node_names"] = self._merge_preferred_labels(
            anchor_gene_names,
            data_x_raw.iloc[:, 0].astype(str).tolist(),
        )
        processed_data["_pathway_names"] = self._resolve_pathway_names(
            [str(column) for column in data_x_raw.columns[1:]]
        )
        if "result_num" in anchor_genes.columns:
            processed_data["_anchor_indices"] = set(
                int(index) for index in anchor_genes.index[anchor_genes["result_num"] == 1]
            )
        else:
            processed_data["_anchor_indices"] = set()

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
        if "omics" in raw_input:
            return self.predict_multiomics(raw_input, include_graph=include_graph)
        return self.predict_base(raw_input, include_graph=include_graph)

    def predict_base(self, raw_input: dict, include_graph: bool = True):
        cancer_type = raw_input.get("cancer_type", "default")
        target_model = self._get_base_model(cancer_type)

        with torch.no_grad():
            data, geo_tensor = preprocess_for_inference(raw_input)
            data = data.to(self.device)
            geo_tensor = geo_tensor.to(self.device)

            result = target_model(data, geo_tensor)
            if "out" in result:
                result["prediction"] = result["out"].argmax(dim=1)
                result["out"] = result["prediction"]

            json_serializable_result = self._to_json_serializable(result)
            self._add_structured_core_results(json_serializable_result, raw_input)
            return self._filter_heavy_outputs(json_serializable_result, include_graph=include_graph)

    def predict_multiomics(self, raw_input: dict, include_graph: bool = True):
        with torch.no_grad():
            data, _ = preprocess_for_inference(raw_input)
            data = data.to(self.device)

            omics = raw_input["omics"]
            x_rna = torch.tensor(omics["data_geo_x"].values, dtype=torch.float).to(self.device)
            x_meth = torch.tensor(omics["data_meth_x"].values, dtype=torch.float).to(self.device)
            x_cnv = torch.tensor(omics["data_cnv_x"].values, dtype=torch.float).to(self.device)
            x_snv = torch.tensor(omics["data_snv_x"].values, dtype=torch.float).to(self.device)

            result = self._get_multiomics_model()(
                data,
                x_rna,
                x_meth=x_meth,
                x_cnv=x_cnv,
                x_snv=x_snv,
            )
            if "out_multiomics" not in result:
                raise RuntimeError("Multi-omics model did not return 'out_multiomics'")

            probabilities = torch.exp(result["out_multiomics"])
            result["out_multiomics_probabilities"] = probabilities
            result["prediction"] = probabilities.argmax(dim=1)
            result["sample_ids"] = omics["sample_ids"]
            result["gene_ids"] = omics["gene_ids"]

            json_serializable_result = self._to_json_serializable(result)
            self._add_structured_core_results(json_serializable_result, raw_input)
            return self._filter_heavy_outputs(json_serializable_result, include_graph=include_graph)

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

    def _add_structured_core_results(self, result: dict, raw_input: dict) -> None:
        node_names = raw_input.get("_node_names", [])
        pathway_names = raw_input.get("_pathway_names", [])
        anchor_indices = raw_input.get("_anchor_indices", set())

        gene_scores = self._flatten_numeric_values(result.get("vimp_g"))
        gene_correlations = self._flatten_numeric_values(result.get("cor"))
        structured_core_genes = []
        for index in self._top_indices(gene_scores):
            structured_core_genes.append({
                "index": index,
                "name": self._label_at(node_names, index, f"gene_{index}"),
                "score": float(gene_scores[index]),
                "correlation": (
                    float(gene_correlations[index])
                    if index < len(gene_correlations)
                    else None
                ),
                "is_anchor": index in anchor_indices,
            })

        pathway_weights = self._flatten_numeric_values(result.get("pw_w"))
        structured_core_pathways = []
        for index in self._top_indices(pathway_weights):
            structured_core_pathways.append({
                "index": index,
                "name": self._label_at(pathway_names, index, f"pathway_{index}"),
                "weight": float(pathway_weights[index]),
            })

        result["structured_core_genes"] = structured_core_genes
        result["structured_core_pathways"] = structured_core_pathways
        result["core_genes"] = [gene["name"] for gene in structured_core_genes]
        result["core_pathways"] = [pathway["name"] for pathway in structured_core_pathways]

    @classmethod
    def _top_indices(cls, values: List[float]) -> List[int]:
        if not values:
            return []
        return sorted(
            range(len(values)),
            key=lambda index: values[index],
            reverse=True,
        )[:cls.CORE_RESULT_LIMIT]

    @staticmethod
    def _flatten_numeric_values(value) -> List[float]:
        if value is None:
            return []
        array = np.asarray(value, dtype=float).reshape(-1)
        return array.tolist()

    @staticmethod
    def _label_at(labels: List[str], index: int, fallback: str) -> str:
        if index < len(labels) and labels[index]:
            return labels[index]
        return fallback

    @classmethod
    def _extract_gene_names(cls, anchor_genes: pd.DataFrame) -> List[str]:
        if anchor_genes.empty:
            return []

        preferred_columns = {
            "gene",
            "genes",
            "gene_name",
            "genename",
            "gene_symbol",
            "genesymbol",
            "symbol",
            "name",
        }
        candidate_columns = sorted(
            anchor_genes.columns,
            key=lambda column: (
                cls._normalized_column_name(column) not in preferred_columns,
                list(anchor_genes.columns).index(column),
            ),
        )

        for column in candidate_columns:
            normalized_column = cls._normalized_column_name(column)
            if normalized_column == "result_num":
                continue

            values = anchor_genes[column].fillna("").astype(str).str.strip()
            if not cls._looks_like_numeric_ids(values):
                return values.tolist()
        return []

    @staticmethod
    def _merge_preferred_labels(
        preferred_labels: List[str],
        fallback_labels: List[str],
    ) -> List[str]:
        label_count = max(len(preferred_labels), len(fallback_labels))
        labels = []
        for index in range(label_count):
            preferred = preferred_labels[index] if index < len(preferred_labels) else ""
            fallback = fallback_labels[index] if index < len(fallback_labels) else ""
            labels.append(preferred or fallback)
        return labels

    @staticmethod
    def _normalized_column_name(column: str) -> str:
        return str(column).strip().lower().replace(" ", "_").replace("-", "_")

    @staticmethod
    def _looks_like_numeric_ids(values: pd.Series) -> bool:
        non_empty_values = values[values != ""]
        if non_empty_values.empty:
            return True
        numeric_ratio = pd.to_numeric(non_empty_values, errors="coerce").notna().mean()
        return numeric_ratio >= 0.95

    @staticmethod
    def _load_pathway_id_labels(path: Path) -> List[str]:
        if not path.exists():
            return []

        pathway_ids = pd.read_csv(path)
        if not {"id", "pwid"}.issubset(pathway_ids.columns):
            return []

        labels = [""] * (int(pathway_ids["id"].max()) + 1)
        for _, row in pathway_ids.iterrows():
            labels[int(row["id"])] = str(row["pwid"])
        return labels

    def _resolve_pathway_names(self, uploaded_names: List[str]) -> List[str]:
        if len(self.pathway_id_labels) >= len(uploaded_names):
            return self.pathway_id_labels[:len(uploaded_names)]
        return uploaded_names
