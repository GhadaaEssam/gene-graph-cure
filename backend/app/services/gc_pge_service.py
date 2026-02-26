# services/gc_pge_service.py

import torch
from model.preprocess import preprocess_for_inference


class GC_PGE_Service:

    def __init__(self, model_path: str):
        """
        Loads full trained model once at startup.
        """

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load entire saved model
        self.model = torch.load(model_path, map_location=self.device)

        self.model.to(self.device)
        self.model.eval()

    def predict(self, raw_input: dict):

        with torch.no_grad():

            # Preprocess input
            data, geo_tensor = preprocess_for_inference(raw_input)

            data = data.to(self.device)
            geo_tensor = geo_tensor.to(self.device)

            # Forward pass
            result = self.model(data, geo_tensor)

            return {
                "prediction": result["out"].cpu().tolist(),
                "node_importance": result["cor"].cpu().tolist(),
                "graph_matrix": result["graph"].cpu().tolist(),
                "feature_weights": result["pw_w"].cpu().tolist()
            }