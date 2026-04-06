# Standard library and file system operations
import os
# PyTorch for deep learning and tensor operations
import torch
import torch.nn as nn
import torch.nn.functional as F
# from torch_geometric.datasets import Planetoid
import torch_geometric.transforms as T
import torch_geometric.nn as pyg_nn
from torch_geometric.data import Data
# Data manipulation and analysis
import pandas as pd
import random
# Scikit-learn for model evaluation metrics
from sklearn.metrics import roc_auc_score, f1_score, average_precision_score,confusion_matrix
from sklearn import model_selection
# Numerical computing
import numpy as np

# Import preprocessing utilities and the main model architecture
from model.preprocess import make_data_geo, get_train_edge, make_data, pgb
from model.model import Model

# Import inverse error function for rank Gaussian normalization
from scipy.special import erfinv 
# Small epsilon value for numerical stability (prevents division by zero)
EPSILON = np.finfo(float).eps


# Utility function to convert genomic data to PyTorch Geometric Data object without labels
def make_data_geo_no_label(data_geo):
    """Convert pandas DataFrame of genomic features to PyTorch Geometric Data object.
    
    Args:
        data_geo: pandas DataFrame with genomic features (samples x genes)
        
    Returns:
        PyTorch Geometric Data object with features only (no labels)
    """
    data = Data()
    # Convert pandas DataFrame to PyTorch tensor for GPU compatibility
    data.X = torch.tensor(data_geo.values, dtype=torch.float)
    return data

def predict_model(model_path, data_geo, anchor_list, data_x, data_ppi_link_index, data_homolog_index, progressBarObj):
    """Load trained model and make drug resistance predictions for test samples.
    
    Args:
        model_path: Path to saved model weights 
        data_geo: Genomic features DataFrame (samples x genes) 
        anchor_list: Known drug response labels for training samples
        data_x: Normalized genomic features for all samples
        data_ppi_link_index: Protein-protein interaction network edges
        data_homolog_index: Gene homology network edges
        progressBarObj: Progress bar object for UI updates
        
    Returns:
        Dictionary with predictions: 'out' (class predictions), 'vimp' (importance scores),
        'graph' (learned adjacency matrix), 'pw_w' (pathway weights)
    """
    print("loading model")
    
    # Apply Rank Gaussian normalization to genomic features
    # Step 1: Normalize to [-1, 1] range
    rankGauss = (data_geo.values / data_geo.values.max() - 0.5) * 2
    # Step 2: Clip to avoid numerical issues at boundaries
    rankGauss = np.clip(rankGauss, -1 + EPSILON, 1 - EPSILON)
    # Step 3: Apply inverse error function for Gaussian transformation
    rankGauss = erfinv(rankGauss)
    # Step 4: Convert back to DataFrame for processing
    data_geo = pd.DataFrame(rankGauss, columns=data_geo.columns)

    # Convert genomic data to PyTorch Geometric format
    data_geo_obj = make_data_geo_no_label(data_geo)

    # Extract indices of known drug response samples (labeled as 1)
    anchor_index = anchor_list.result_num[anchor_list.result_num == 1].index
    # Split into training and test sets (80/20 split)
    train_anchor, test_anchor = model_selection.train_test_split(anchor_index, test_size=0.2)
    # Save test set for later verification and analysis
    test_anchor_csv = pd.DataFrame(test_anchor, dtype=int)
    test_anchor_csv.to_csv(r'result/test_anchor.csv')

    # Re-extract anchor indices for final train set computation
    anchor_index = anchor_list.result_num[anchor_list.result_num == 1].index
    # Create training set by removing test samples from all anchors
    train_anchor = pd.Series(list(set(anchor_index.to_list()) - set(test_anchor.to_list())))

    # Load Protein-Protein Interaction network for training samples
    print("loading ppi network")
    # Create progress bar for PPI loading (0-70% of total)
    pgb1 = pgb(progressBarObj, 0, 70)
    # Extract PPI edges involving training samples only (for training data context)
    train_edge_ppi, _ = get_train_edge(data_ppi_link_index, train_anchor, pgb1)
    
    # Load Gene Homology network for training samples
    print("loading homolog network")
    # Create progress bar for homolog loading (70-100% of total)
    pgb2 = pgb(progressBarObj, 70, 100)
    # Extract homolog edges involving training samples only
    train_edge_homolog, _ = get_train_edge(data_homolog_index, train_anchor, pgb2)
    

    # Create graph data object with genomic features, network edges, and labels
    data_obj = make_data(data_x, train_edge_ppi, train_edge_homolog, anchor_list, test_anchor)

    #os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # 配置GPU

    # COMMENTED BY GENE GRAPH CURE TEAM
    # my_net = torch.load(model_path)
    
    # UPDATED BY GENE GRAPH CURE TEAM
    my_net = torch.load(model_path, weights_only=False)

    # Detect available hardware and move model to device (GPU if available, CPU otherwise)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Transfer model to device
    my_net = my_net.to(device)
    # Transfer graph data to device
    data = data_obj.to(device)
    # Transfer genomic features to device
    data_geo_obj = data_geo_obj.to(device)

    # Set model to evaluation mode (disables dropout, batch norm updates)
    my_net.eval()

    # Forward pass: predict on test samples using both graph and genomic data
    result = my_net(data, data_geo_obj.X)

    # Extract and return predictions and explanation scores
    return {
        # 'out': Drug resistance class predictions (0=susceptible, 1=resistant)
        "out": result['out'].max(dim=1).indices.detach().cpu(),
        # 'vimp': Gene/node importance scores from graph neural network
        "vimp": result['cor'].detach().cpu(),
        # 'graph': Learned adjacency matrix showing gene-to-gene relationships
        "graph": result['graph'].detach().cpu().numpy(),
        # 'pw_w': Pathway importance weights for explainability
        "pw_w": result['pw_w'].detach().cpu()
    }