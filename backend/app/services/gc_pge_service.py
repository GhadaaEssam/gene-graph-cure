import torch
import pandas as pd
import io
from pathlib import Path
import sys

# --- Module path setup ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "gcpge"))

import model
sys.modules["model.model"] = model  

from gcpge.preprocess import preprocess_for_inference

class GC_PGE_Service:
    def __init__(self, model_path: str):
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model weights not found at: {model_path}")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load model once
        self.model = torch.load(
            model_path,
            map_location=self.device,
            weights_only=False
        )
        self.model.to(self.device)
        self.model.eval()

    async def predict_from_files(self, files_dict: dict):
        """
        Mirrors the original research model's data handling logic.
        """
        processed_data = {}
        
        # 1. Read the files from the streams
        contents = {key: await f.read() for key, f in files_dict.items()}

        # --- Mirroring the GUI logic exactly ---
        
        # [lineEdit_2] Sample expression matrix: First col is name, rest is data
        data_sample = pd.read_csv(io.BytesIO(contents["geo_features"]), header=0)
        # Research code: sample_name = data_sample.iloc[:, 0] (ignored for math)
        processed_data["geo_features"] = data_sample.iloc[:, 1:] 

        # [lineEdit_3] Characteristic genes (Anchor list)
        processed_data["anchor_genes"] = pd.read_csv(io.BytesIO(contents["anchor_genes"]), header=0)

        # [lineEdit_4] Signal path network (data_x): First col is ID, rest is data
        data_x_raw = pd.read_csv(io.BytesIO(contents["node_features"]), header=0)
        processed_data["node_features"] = data_x_raw.iloc[:, 1:]

        # [lineEdit_5] PPI network
        processed_data["ppi_edges"] = pd.read_csv(io.BytesIO(contents["ppi_edges"]), header=0)

        # [lineEdit_6] Same origin network (Homolog)
        processed_data["homolog_edges"] = pd.read_csv(io.BytesIO(contents["homolog_edges"]), header=0)

        # 2. Call the prediction logic with the correctly sliced DataFrames
        return self.predict(processed_data)

    def predict(self, raw_input: dict):
        """
        Modified to ensure data types match what preprocess_for_inference expects.
        """
        # (Internal logic remains similar, ensuring your preprocess_for_inference 
        # accepts DataFrames as inputs instead of just Lists)
        
        with torch.no_grad():
            # we just parsed from the CSVs.
            data, geo_tensor = preprocess_for_inference(raw_input)

            data = data.to(self.device)
            geo_tensor = geo_tensor.to(self.device)

            # Forward pass
            result = self.model(data, geo_tensor)

            # Convert tensors to Python lists for JSON response
            return {
                "prediction": result["out"].detach().cpu().tolist(),
                "node_importance": result["cor"].detach().cpu().tolist(),
                "graph_matrix": result["graph"].detach().cpu().tolist(),
                "feature_weights": result["pw_w"].detach().cpu().tolist()
            }