import torch
from torch_geometric.data import Data
import pandas as pd
import random
from sklearn import model_selection
import numpy as np

# Module: preprocessing helpers for graph-based datasets
# Contains small utilities to prepare torch-geometric Data objects,
# perform K-fold splitting for tabular GEO features, and split edge lists
# into train/test portions based on anchor sets.

class pgb():
    """Progress bar bridge class.
    Wraps an external signal-emitting object to convert a normalized
    progress value (0..1) into an integer scaled value for the UI.
    """
    def __init__(self,signalObj,min_value,max_value):
        self.min_value = min_value
        self.scale = max_value-min_value
        self.signalObj = signalObj
    def update(self,n_value):
        # n_value is expected in [0,1]; scale and emit integer for UI
        self.signalObj.emit(int(n_value*self.scale + self.min_value))

def make_data_geo(data_geo, label_geo,k,i,seed):
    """Create a k-fold split for GEO-style tabular features.

    Args:
        data_geo (pd.DataFrame): features, rows correspond to samples
        label_geo (pd.Series/DataFrame): labels aligned with data_geo
        k (int): number of folds (>1)
        i (int): index of the fold to use as validation (0-based)
        seed (int): random seed for reproducible shuffling

    Returns:
        torch_geometric.data.Data: object with X_train, X_test, Y_train, Y_test tensors
    """
    # K-fold split for GEO features
    assert k > 1

    data = Data()
    # Reproducible shuffle of indices
    np.random.seed(seed)
    indices = np.random.permutation(range(len(label_geo)))
    # X = data_geo.loc[indices]
    # Y = label_geo.loc[indices]
    X = torch.tensor(data_geo.loc[indices].values,dtype=torch.float)
    Y = torch.tensor(label_geo.loc[indices].values,dtype=torch.int)

    # Compute fold boundaries (integer division)
    fold_size = X.shape[0] // k
    X_train, Y_train = None, None
    for j in range(k):
        # slice selects the j-th fold range
        idx = slice(j * fold_size, (j + 1) * fold_size)  # slice(start,end,step)
        X_part, y_part = X[idx, :], Y[idx]
        if j == i:  # the i-th fold is held out as validation/test
            X_test, Y_test = X_part, y_part
        elif X_train is None:
            X_train, Y_train = X_part, y_part
        else:
            # concatenate remaining folds to form training set (stack rows)
            X_train = torch.cat((X_train, X_part), dim=0) # dim=0 concatenates rows
            Y_train = torch.cat((Y_train, y_part), dim=0)

    data.X_train= X_train
    data.X_test= X_test
    data.Y_train= Y_train
    data.Y_test= Y_test

    # pd.DataFrame(X_test).to_csv(r'result/X_test.csv')
    # pd.DataFrame(Y_test).to_csv(r'result/Y_test.csv')
    return data

def get_train_edge(data_edge_index, train_anchor, pgb):
    """Split an edge-list (DataFrame) into train and test edges based on anchor membership.

    Rules:
    - If both endpoints are in train_anchor => train edge
    - If exactly one endpoint is in train_anchor => test edge
    - Edges with neither endpoint in train_anchor are ignored here

    Args:
        data_edge_index (pd.DataFrame): edge list with at least two columns [src, dst]
        train_anchor (pd.Series or iterable): node indices considered anchors (train set)
        pgb (pgb): progress bridge used to emit progress occasionally

    Returns:
        (pd.DataFrame, pd.DataFrame): (train_edge_index, test_edge_index)
    """
    train_edge_index = pd.DataFrame(dtype=int)
    test_edge_index = pd.DataFrame(dtype=int)

    for i in range(len(data_edge_index)):
        if(i%1000 == 0):
            # print(i/len(data_edge_index))
            pgb.update(i/len(data_edge_index))
        # Check membership of both endpoints in the train_anchor set
        if (data_edge_index.iloc[i,0] in train_anchor.values) and (data_edge_index.iloc[i,1] in train_anchor.values):
            train_edge_index = train_edge_index.append(data_edge_index.iloc[i,:])
        elif(data_edge_index.iloc[i,0] in train_anchor.values) or (data_edge_index.iloc[i,1] in train_anchor.values):
            # edges crossing between anchor and non-anchor are test edges
            test_edge_index = test_edge_index.append(data_edge_index.iloc[i,:])
    return train_edge_index , test_edge_index

def make_data(data_x,data_ppi_link_index,data_homolog_index,anchor_list,test_anchor):
    """Assemble a torch_geometric Data object for a graph-based dataset.

    Steps:
    - Determine anchor and non-anchor node indices
    - Build training and test masks (boolean masks per node)
    - Construct edge_index dict for different edge types ('ppi', 'homolog')
    - Convert pandas structures into torch tensors expected by torch_geometric

    Args:
        data_x (pd.DataFrame): node features, indexed by node id
        data_ppi_link_index (pd.DataFrame): PPI edges as two-column dataframe
        data_homolog_index (pd.DataFrame): homolog edges as two-column dataframe
        anchor_list (pd.DataFrame): contains result_num column indicating anchors (1) or not (0)
        test_anchor (iterable): nodes reserved for testing anchors

    Returns:
        torch_geometric.data.Data: populated graph object with x, edge_index, y, masks, etc.
    """
    # anchor indices where result_num == 1
    anchor_index = anchor_list.result_num[anchor_list.result_num==1].index
    not_anchor_index = anchor_list.result_num[anchor_list.result_num==0].index

    # train_anchor excludes nodes reserved for testing
    train_anchor= pd.Series(list(set(anchor_index.to_list())-set(test_anchor.to_list())))
    not_train_anchor = pd.Series(list(set(anchor_list.index)-set(train_anchor.to_list())))

    # Build label vector: 1 for anchors, 0 otherwise
    data_y = pd.Series(0,index=data_x.index,dtype=int)
    data_y[anchor_index.to_list()]=1

    # test_sample = random.sample(not_anchor_index.to_list(),len(anchor_index))
    test_sample = random.sample(not_train_anchor.to_list(),len(train_anchor))

    # train mask: True for train_anchor plus the sampled negatives
    data_train_mask = pd.Series(False,index=data_x.index,dtype=bool)
    data_train_mask[train_anchor.to_list()]=True
    data_train_mask[test_sample]=True

    # data_test_mask = pd.Series(False,index=data_x.index,dtype=bool)
    # data_test_mask[test_anchor.to_list()]=True
    # data_test_mask[test_sample[len(train_anchor):]]=True
    data_test_mask = pd.Series(True,index=data_x.index,dtype=bool)
    data_test_mask[data_train_mask]=False

    data = Data()
    data.num_nodes = len(data_x)
    data.num_node_features = data_x.shape[1]
    # Build edge_index entries as long tensors in [2, num_edges] shape expected by torch_geometric
    data.edge_index = {
                       'ppi':torch.tensor(data_ppi_link_index.T.values,dtype=torch.long),
                       'homolog':torch.tensor(data_homolog_index.T.values,dtype=torch.long)
                       }

    data.x = torch.tensor(data_x.values,dtype=torch.float)
    data.y = torch.tensor(data_y.values,dtype=torch.int)
    data.train_mask = torch.tensor(data_train_mask.values,dtype=torch.bool)
    data.test_mask = torch.tensor(data_test_mask.values,dtype=torch.bool)
    return data


from scipy.special import erfinv
import numpy as np
import torch
from torch_geometric.data import Data

EPSILON = 1e-6


def preprocess_for_inference(raw_input):
    # Helper to convert potential DataFrames/Series to numpy/tensors
    def to_df_values(key):
        val = raw_input[key]
        # If it's a Pandas object, get the underlying values
        return val.values if hasattr(val, 'values') else val

    # --- Node features ---
    node_feat = to_df_values("node_features")
    # If the CSV has an index column (like Gene Name), remove it before tensor conversion
    if node_feat.shape[1] > 1 and isinstance(node_feat, np.ndarray):
        # Assuming first column might be names if it's not all floats
        # You may need to adjust this based on your CSV structure
        pass 

    x = torch.tensor(node_feat, dtype=torch.float)
    num_nodes = x.size(0)

    # --- Edge indices ---
    # Ensure these are purely integer indices for PyG
    ppi_val = to_df_values("ppi_edges")
    homolog_val = to_df_values("homolog_edges")
    
    edge_index_ppi = torch.tensor(ppi_val, dtype=torch.long).t().contiguous()
    edge_index_homolog = torch.tensor(homolog_val, dtype=torch.long).t().contiguous()

    # --- Anchor genes (Mirroring GUI behavior) ---
    anchor_df = raw_input.get("anchor_genes")

    # The original research code used:
    # anchor_index = anchor_list.result_num[anchor_list.result_num == 1].index
    if hasattr(anchor_df, "columns") and "result_num" in anchor_df.columns:
        # Filter rows where result_num is 1, then get their indices
        anchor_indices = anchor_df[anchor_df["result_num"] == 1].index.tolist()
    elif hasattr(anchor_df, "tolist"):
        # Fallback if it was already converted to a list/series elsewhere
        anchor_indices = anchor_df.tolist()
    else:
        anchor_indices = list(anchor_df)

    # Convert to set for O(1) lookup
    anchor_indices_set = set(anchor_indices)

    train_mask = torch.zeros(num_nodes, dtype=torch.bool)
    labels = torch.zeros(num_nodes, dtype=torch.long)

    for idx in anchor_indices:
        try:
            i = int(idx) # Ensure it's an int
            if i < num_nodes:
                train_mask[i] = True
                labels[i] = 1
        except (ValueError, TypeError):
            continue

    test_mask = ~train_mask

    # --- Graph object ---
    data = Data()
    data.num_nodes = num_nodes
    data.num_node_features = x.size(1)
    data.x = x
    data.y = labels
    data.train_mask = train_mask
    data.test_mask = test_mask
    data.edge_index = {
        "ppi": edge_index_ppi,
        "homolog": edge_index_homolog
    }

    # --- GEO features ---
    geo_val = to_df_values("geo_features")
    geo_array = np.array(geo_val, dtype=np.float32)

    # Normalize and Rank-Gaussian
    denom = np.max(np.abs(geo_array)) + EPSILON
    geo_array = geo_array / denom
    geo_array = np.clip(geo_array, -1 + EPSILON, 1 - EPSILON)
    geo_array = erfinv(geo_array)

    geo_tensor = torch.tensor(geo_array, dtype=torch.float)

    return data, geo_tensor