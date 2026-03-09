import os
import torch

# Import model classes from model.py in the same folder
from model import *

# Dynamic path to the model file
base_dir = os.path.dirname(__file__)
model_path = os.path.join(base_dir, "liver_model.pt")

# Load the model
m = torch.load(model_path, map_location="cpu", weights_only=False)

# Extract number of nodes and geo feature dimension
N = m.mutiGAT.generalization.dfr.logit_p.shape[0]
G = m.vdMLP_list[0].model[0].in_features

print(f"N (nodes): {N}")
print(f"G (geo features): {G}")