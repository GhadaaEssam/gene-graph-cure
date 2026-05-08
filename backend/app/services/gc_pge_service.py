import torch
import pandas as pd
import io
import numpy as np
from pathlib import Path
import sys

# --- Module path setup ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "gcpge"))

import model
sys.modules["model.model"] = model  

from gcpge.preprocess import preprocess_for_inference

class GC_PGE_Service:
    CORE_RESULT_LIMIT = 10
    STATIC_INPUT_FILENAMES = {
        "anchor_genes": "anchor_genes.csv",
        "node_features": "node_features.csv",
        "ppi_edges": "ppi_edges.csv",
        "homolog_edges": "homolog_edges.csv",
    }

    def __init__(self, model_path: str):

        # Validate model path at initialization
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model weights not found at: {model_path}")

        # Set device (GPU if available, else CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.pathway_id_labels = self._load_pathway_id_labels(
            PROJECT_ROOT / "gcpge" / "pw_id.csv"
        )

        # Load model once
        self.model = torch.load(
            model_path,
            map_location=self.device,
            weights_only=False
        )

        # Move model to device and set to eval mode
        self.model.to(self.device)
        self.model.eval()

    async def predict_from_files(self, files_dict: dict):
        """
        Mirrors the original research model's data handling logic.
        """
        contents = {key: await f.read() for key, f in files_dict.items()}
        data_sample = pd.read_csv(io.BytesIO(contents["geo_features"]), header=0)
        anchor_genes = pd.read_csv(io.BytesIO(contents["anchor_genes"]), header=0)
        data_x_raw = pd.read_csv(io.BytesIO(contents["node_features"]), header=0)
        ppi_edges = pd.read_csv(io.BytesIO(contents["ppi_edges"]), header=0)
        homolog_edges = pd.read_csv(io.BytesIO(contents["homolog_edges"]), header=0)

        processed_data = self._prepare_input_data(
            data_sample=data_sample,
            anchor_genes=anchor_genes,
            data_x_raw=data_x_raw,
            ppi_edges=ppi_edges,
            homolog_edges=homolog_edges,
        )

        return self.predict(processed_data)

    async def predict_from_geo_file(self, geo_features, static_inputs_dir: Path):
        """
        Runs prediction with patient-specific GEO features and static model inputs
        stored on disk for the selected model.
        """
        self._validate_static_inputs(static_inputs_dir)

        geo_contents = await geo_features.read()
        data_sample = pd.read_csv(io.BytesIO(geo_contents), header=0)
        anchor_genes = pd.read_csv(
            static_inputs_dir / self.STATIC_INPUT_FILENAMES["anchor_genes"],
            header=0,
        )
        data_x_raw = pd.read_csv(
            static_inputs_dir / self.STATIC_INPUT_FILENAMES["node_features"],
            header=0,
        )
        ppi_edges = pd.read_csv(
            static_inputs_dir / self.STATIC_INPUT_FILENAMES["ppi_edges"],
            header=0,
        )
        homolog_edges = pd.read_csv(
            static_inputs_dir / self.STATIC_INPUT_FILENAMES["homolog_edges"],
            header=0,
        )

        processed_data = self._prepare_input_data(
            data_sample=data_sample,
            anchor_genes=anchor_genes,
            data_x_raw=data_x_raw,
            ppi_edges=ppi_edges,
            homolog_edges=homolog_edges,
        )

        return self.predict(processed_data)

    def _prepare_input_data(
        self,
        data_sample: pd.DataFrame,
        anchor_genes: pd.DataFrame,
        data_x_raw: pd.DataFrame,
        ppi_edges: pd.DataFrame,
        homolog_edges: pd.DataFrame,
    ) -> dict:
        processed_data = {}

        # Sample expression matrix: First col is name, rest is data
        processed_data["geo_features"] = data_sample.iloc[:, 1:]

        # Characteristic genes (Anchor list)
        processed_data["anchor_genes"] = anchor_genes
        processed_data["_anchor_gene_names"] = self._extract_gene_names(anchor_genes)

        # Signal path network (data_x): First col is ID, rest is data
        processed_data["node_features"] = data_x_raw.iloc[:, 1:]
        processed_data["_node_names"] = self._merge_preferred_labels(
            processed_data["_anchor_gene_names"],
            data_x_raw.iloc[:, 0].astype(str).tolist()
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

        processed_data["ppi_edges"] = ppi_edges
        processed_data["homolog_edges"] = homolog_edges

        return processed_data

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

    def predict(self, raw_input: dict):
        """
        Runs inference and returns all output keys from the model as JSON-serializable lists.
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
                    if key == "out":
                        value = value.max(dim=1).indices
                    # Detach, move to CPU, and convert to nested list
                    json_serializable_result[key] = value.detach().cpu().tolist()
                elif isinstance(value, (np.ndarray, np.generic)):
                    # Handle any numpy arrays that might be in the output
                    json_serializable_result[key] = value.tolist()
                else:
                    # Keep native Python types (ints, floats, lists) as is
                    json_serializable_result[key] = value

            self._add_structured_core_results(json_serializable_result, raw_input)
            return json_serializable_result

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
    def _top_indices(cls, values: list[float]) -> list[int]:
        if not values:
            return []
        return sorted(
            range(len(values)),
            key=lambda index: values[index],
            reverse=True
        )[:cls.CORE_RESULT_LIMIT]

    @staticmethod
    def _flatten_numeric_values(value) -> list[float]:
        if value is None:
            return []
        array = np.asarray(value, dtype=float).reshape(-1)
        return array.tolist()

    @staticmethod
    def _label_at(labels: list[str], index: int, fallback: str) -> str:
        if index < len(labels) and labels[index]:
            return labels[index]
        return fallback

    @classmethod
    def _extract_gene_names(cls, anchor_genes: pd.DataFrame) -> list[str]:
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
            )
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
        preferred_labels: list[str],
        fallback_labels: list[str]
    ) -> list[str]:
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
    def _load_pathway_id_labels(path: Path) -> list[str]:
        if not path.exists():
            return []

        pathway_ids = pd.read_csv(path)
        if not {"id", "pwid"}.issubset(pathway_ids.columns):
            return []

        labels = [""] * (int(pathway_ids["id"].max()) + 1)
        for _, row in pathway_ids.iterrows():
            labels[int(row["id"])] = str(row["pwid"])
        return labels

    def _resolve_pathway_names(self, uploaded_names: list[str]) -> list[str]:
        if len(self.pathway_id_labels) >= len(uploaded_names):
            return self.pathway_id_labels[:len(uploaded_names)]
        return uploaded_names
