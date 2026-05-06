import pandas as pd

def load_results(base_path=""):

    prediction = pd.read_csv(f"{base_path}/predict_out.csv", header=None)
    probability = pd.read_csv(f"{base_path}/predict_muti_all.csv", header=None)
    pathways = pd.read_csv(f"{base_path}/pw_w.csv", header=None)
    graph = pd.read_csv(f"{base_path}/graph.csv", header=None)

    return {
        "prediction": int(prediction.iloc[0, 0]),
        "probability": float(probability.iloc[0, 0]),
        "pathway_weights": pathways.values.flatten().tolist(),
        "graph": graph.values.tolist()
    }