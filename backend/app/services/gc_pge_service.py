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
        processed_data = {}
        
        # 1. Read the files from the streams
        contents = {key: await f.read() for key, f in files_dict.items()}
        
        # Sample expression matrix: First col is name, rest is data
        data_sample = pd.read_csv(io.BytesIO(contents["geo_features"]), header=0)
        processed_data["geo_features"] = data_sample.iloc[:, 1:] 

        # Characteristic genes (Anchor list)
        anchor_genes = pd.read_csv(io.BytesIO(contents["anchor_genes"]), header=0)
        processed_data["anchor_genes"] = anchor_genes

        # Signal path network (data_x): First col is ID, rest is data
        data_x_raw = pd.read_csv(io.BytesIO(contents["node_features"]), header=0)
        processed_data["node_features"] = data_x_raw.iloc[:, 1:]
        processed_data["_node_names"] = data_x_raw.iloc[:, 0].astype(str).tolist()
        processed_data["_pathway_names"] = self._resolve_pathway_names(
            [str(column) for column in data_x_raw.columns[1:]]
        )
        if "result_num" in anchor_genes.columns:
            processed_data["_anchor_indices"] = set(
                int(index) for index in anchor_genes.index[anchor_genes["result_num"] == 1]
            )
        else:
            processed_data["_anchor_indices"] = set()

        # PPI network
        processed_data["ppi_edges"] = pd.read_csv(io.BytesIO(contents["ppi_edges"]), header=0)

        # Same origin network (Homolog)
        processed_data["homolog_edges"] = pd.read_csv(io.BytesIO(contents["homolog_edges"]), header=0)

        # 2. Call the prediction logic with the correctly sliced DataFrames
        return self.predict(processed_data)

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
