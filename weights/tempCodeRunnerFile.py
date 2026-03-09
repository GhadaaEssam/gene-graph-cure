import torch

m = torch.load("immunotherapy_model.pt", map_location="cpu", weights_only=False)

N = m.mutiGAT.generalization.dfr.logit_p.shape[0]  # number of nodes
G = m.vdMLP_list[0].model[0].in_features            # geo feature dim

print(f"N (nodes): {N}")
print(f"G (geo features): {G}")