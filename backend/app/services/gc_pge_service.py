import torch
from model.model import Model
from model.preprocess import preprocess_for_inference


class GC_PGE_Service:

    def __init__(self, model_path: str, model_config: dict):

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Build model with correct parameters
        self.model = Model(
            data_geo_x_shape=model_config["data_geo_x_shape"],
            num_muti_gat=model_config["num_muti_gat"],
            num_muti_mlp=model_config["num_muti_mlp"],
            num_node_features=model_config["num_node_features"],
            data_x_N=model_config["data_x_N"]
        )

        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def predict(self, raw_input: dict):

        with torch.no_grad():

            # Preprocess
            data, geo_tensor = preprocess_for_inference(raw_input)

            data = data.to(self.device)
            geo_tensor = geo_tensor.to(self.device)

            # Forward pass
            result = self.model(data, geo_tensor)

            # Convert tensors to JSON-safe format
            output = {
                "prediction": result["out"].cpu().tolist(),
                "node_importance": result["cor"].cpu().tolist(),
                "graph_matrix": result["graph"].cpu().tolist(),
                "feature_weights": result["pw_w"].cpu().tolist()
            }

        return output