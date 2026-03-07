# services/gc_pge_service.py
import torch
from pathlib import Path
import sys

# --- Module path setup and fake module registration ---
# Must happen BEFORE torch.load to ensure model class can be unpickled
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "gcpge"))  # insert at front, not append

import model
sys.modules['model.model'] = model  # fake module to match checkpoint's pickle path

from gcpge.preprocess import preprocess_for_inference


class GC_PGE_Service:

    def __init__(self, model_path: str):
        """
        Loads full trained model once at startup.
        model_path: absolute path to .pt weights file (injected from predict.py)
        """
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model weights not found at: {model_path}")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load entire saved model (weights_only=False required for full model pickle)
        self.model = torch.load(model_path, map_location=self.device, weights_only=False)
        self.model.to(self.device)
        self.model.eval()

    def predict(self, raw_input: dict):
        # Validate required keys before preprocessing
        required_keys = {"node_features", "ppi_edges", "homolog_edges", "geo_features"}
        missing = required_keys - raw_input.keys()
        if missing:
            raise ValueError(f"Missing required input keys: {missing}")

        with torch.no_grad():
            # Preprocess: applies rank-gaussian to geo, builds Data object
            data, geo_tensor = preprocess_for_inference(raw_input)

            data = data.to(self.device)
            geo_tensor = geo_tensor.to(self.device)

            # Forward pass
            result = self.model(data, geo_tensor)

            return {
                "prediction": result["out"].cpu().tolist(),           # [num_nodes, 2]
                "node_importance": result["cor"].cpu().tolist(),       # [num_nodes]
                "graph_matrix": result["graph"].cpu().tolist(),        # [num_nodes, num_nodes]
                "feature_weights": result["pw_w"].cpu().tolist()       # shape TBD
            }