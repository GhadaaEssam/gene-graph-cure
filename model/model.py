# PyTorch core modules for neural network construction
import torch
import torch.nn as nn
import torch.nn.functional as F

# from torch_geometric.datasets import Planetoid
import torch_geometric.nn as pyg_nn
import numpy as np

# Small epsilon value to prevent numerical instability (division by zero, log(0))
EPSILON = np.finfo(float).eps

# Multi-GAT (Graph Attention Network) Class
# This class combines multiple GAT layers to process graph data with different edge types (PPI, Homolog)
# It outputs drug resistance predictions and creates a generalized graph representation
class MutiGAT(nn.Module):
    def __init__(self,num_muti_gat,num_node_features, hid_c, out_c,data_x_N):
        super(MutiGAT,self).__init__()
        self.num_muti_gat = num_muti_gat  # Number of GAT modules to ensemble
        # self.num_muti_graph = num_muti_graph

        self.data_x_N = data_x_N  # Total number of genes/nodes in the dataset
        self.gat_list = []

        # Edge types representing different biological relationships
        self.edge_type_list = ["ppi","homolog"]  # PPI: protein-protein interactions, Homolog: gene homology

        # self.edge_type_list = ["cor","ppi","homolog"]
        # self.graph_list= []
        
        for i in range(num_muti_gat):
            self.gat_list.append(GraphCNN(in_c=num_node_features, hid_c = hid_c, out_c=out_c))
        # for i in range(num_muti_graph):
        #     self.graph_list.append(GraphCNN_Generalization(in_c=num_node_features, hid_c=hid_c, out_c=out_c,data_x_N=data_x_N))
        
        self.gat_list = nn.ModuleList(self.gat_list)
        # self.graph_list = nn.ModuleList(self.graph_list)
        self.CrossEntropyLoss = nn.CrossEntropyLoss()
        # Generalization module to create a unified graph representation from GAT outputs
        self.generalization = GeneralizationGraph(embedding_dim = 4,data_x_shape = data_x_N,num_node_features=num_node_features)
        
        
    def forward(self,data):
        # Initialize output tensor with shape matching labels, initialize loss accumulator
        out = torch.zeros_like(data.y)
        loss = torch.Tensor([0.]).to(next(self.parameters()).device)
        i = 0
        # graph_loss = torch.Tensor([0.]).to(next(self.parameters()).device)
        # graph = torch.zeros(self.data_x_N,self.data_x_N,dtype=torch.float32).to(next(self.parameters()).device)

        for module in self.gat_list:
            # Each module processes data using a specific edge type (alternating between PPI and Homolog)
            temp,temp_loss = module(data,self.edge_type_list[(i%2)])  # Get predictions and loss from current GAT
            i=i+1
            out = out + temp[:,1].exp()  # Sum exponential of resistance class probabilities (column 1)
            loss = loss + temp_loss  # Accumulate losses across modules
        
        # Generate a generalized graph representation and normalized probabilities
        out_graph,graph,pw_w = self.generalization(data.x,out/(self.num_muti_gat))
        
        # Return averaged predictions, loss, generalized graph output, adjacency matrix, and feature importance
        return out/(self.num_muti_gat), loss/self.num_muti_gat, out_graph[:,1], graph,pw_w


# Graph Convolutional Neural Network with Generalization
# This class applies GAT layers to learn graph representations and includes a generalization module
class GraphCNN_Generalization(nn.Module):
    def __init__(self, in_c, hid_c, out_c,data_x_N):
        super(GraphCNN_Generalization, self).__init__()  # 表示子类GraphCNN继承了父类nn.Module的所有属性和方法
        # self.dfr = ConcreteDropout(in_c,temp= 1.0/10.0)
        self.conv1 = pyg_nn.GATConv(in_channels=in_c, out_channels=hid_c, dropout=0.6 ,heads=1, concat=False)
        # Batch normalization after first GAT layer for training stability
        self.bn1   = nn.BatchNorm1d(hid_c)
        # Second GAT layer: maps hidden features to output dimension (2 classes: resistant/susceptible)
        self.conv2 = pyg_nn.GATConv(in_channels=hid_c, out_channels=out_c, dropout=0.6, heads=1, concat=False)
        # Generalization module to create unified predictions
        self.generalization = GeneralizationGraph(embedding_dim = 4,data_x_shape = data_x_N,num_node_features=in_c)
        
    def forward(self, data):
        # Extract node features: [N, C] where N=number of nodes, C=feature dimension
        x = data.x
        # Extract edge indices: [2, E] where E=number of edges
        edge_index = data.edge_index
        
        # Apply dropout to input features for regularization
        x = F.dropout(x, p=0.6, training=self.training)
        # First GAT layer: learn initial graph representations with attention
        hid = self.conv1(x=x, edge_index=edge_index)
        # Batch normalize hidden representation
        hid = self.bn1(hid)
        # Apply LeakyReLU activation for non-linearity
        hid = F.leaky_relu(hid)
        # Second GAT layer: produce final output predictions
        out = self.conv2(x=hid, edge_index=edge_index)
        # Apply log softmax for numerical stability in classification
        out = F.log_softmax(out, dim=1)
        
        # Pass through generalization module for unified graph representation
        out1,graph = self.generalization(data.x,out[:,1].exp())
        # loss = 0
        # mask = torch.rand(data.train_mask.shape[0])<0.5
        # loss = F.nll_loss(out1[mask],(out[:,1].exp()>=0.5).to(dtype=torch.long)[mask])
        loss1 = F.nll_loss(out[data.train_mask],data.y[data.train_mask].long())
        
        return out1,loss1,graph


# Generalization Graph Module
# Combines model predictions with feature embeddings to create a unified graph representation
# Uses learned weights to emphasize important features for drug resistance prediction
class GeneralizationGraph(nn.Module):
    def __init__(self,embedding_dim,data_x_shape,num_node_features):
        super(GeneralizationGraph, self).__init__()
        # Learnable weight vector for each feature dimension
        self.embedding_w = nn.Parameter(torch.zeros(num_node_features))
        # self.embedding_vec = nn.Parameter(torch.zeros(data_x_shape,embedding_dim))
        self.dfr = ConcreteDropout(num_node_features)
        
    def forward(self,data,node_p):
        # Apply concrete dropout to get features weighted by importance
        embedding_data,pw_vimp = self.dfr(data)
        # Apply sigmoid to create normalized weights for features (0 to 1)
        embedding_w = torch.sigmoid(self.embedding_w)
        # Scale features by learned importance weights
        expanded_data = embedding_data*embedding_w
        
        # expanded_data = torch.cat((embedding_data,self.embedding_vec),dim=1)
        
        # graph_raw = torch.mm(data,data.t())/(data.sum(dim=1)+1e-6)
        graph = torch.mm(expanded_data,expanded_data.t())/(expanded_data.sum(dim=1)+1e-6)
        
        # Reshape node probabilities to column vector for matrix multiplication
        expanded_node_p = node_p.reshape(node_p.shape[0],1)
        # Propagate resistance probabilities through the graph
        adj_node_p = torch.mm(graph,expanded_node_p)
        # Propagate susceptibility probabilities through the graph
        adj_node_p_nag = torch.mm(graph,1-expanded_node_p)
        # Concatenate resistance and susceptibility probabilities
        node_p_combanded = torch.cat((adj_node_p_nag,adj_node_p),dim=1)
        # Normalize to probability distribution across classes
        norm_node_p = F.softmax(node_p_combanded,dim=1)
        
        return norm_node_p,graph,pw_vimp

        

# Concrete Dropout Module
# Implements learned, concrete dropout using the Gumbel-Sigmoid trick
# Learns optimal dropout rates per feature dimension instead of using fixed rates
class ConcreteDropout(nn.Module):
    def __init__(self,shape,temp= 1.0/10.0):
        super().__init__()
        # Learnable logit for each feature - drives dropout rates during training
        self.logit_p = nn.Parameter(torch.zeros(shape))
        # Temperature parameter for Gumbel-Sigmoid: lower temp = sharper transitions
        self.temp = temp
        
    def forward(self,x):
        # Generate different dropout masks during training vs inference
        if self.training:
            # During training: use random uniform noise for stochastic dropout
            unif_noise = torch.rand_like(self.logit_p)
            # unif_noise = torch.full_like(self.logit_p, 0.5)
        else:
            # During inference: use deterministic dropout (0.5 -> no randomness)
            unif_noise = torch.full_like(self.logit_p, 0.5)
        
        # Convert logits to dropout probabilities using sigmoid
        dropout_p = torch.sigmoid(self.logit_p)
        
        # Apply Gumbel-Sigmoid trick to make dropout differentiable
        # This creates a soft approximation of discrete dropout
        approx = (
            torch.log(dropout_p + EPSILON)
            - torch.log(1. - dropout_p + EPSILON)
            + torch.log(unif_noise + EPSILON)
            - torch.log(1. - unif_noise + EPSILON)
        )
        # Apply sigmoid with temperature scaling
        approx_output = torch.sigmoid(approx / self.temp)
        
        # Apply dropout mask to input: multiply by (1 - dropout) probability
        # Return both dropped features and importance weights (1 - dropout_p)
        return x*(1 - approx_output), (1-dropout_p)
    

# Variable Dropout Multi-Layer Perceptron
# Uses learned feature importance (from concrete dropout) to adaptively mask input features
# Combines MLP predictions with attention-weighted features for drug resistance classification
class VariableDropoutMLP(nn.Module):
    def __init__(self,data_x_shape,temp= 1.0/10.0):
        super().__init__()
        # Multi-layer perceptron with decreasing layer sizes and heavy dropout
        self.model = nn.Sequential(
            nn.Linear(data_x_shape,1000),  # Input layer to first hidden layer
            nn.BatchNorm1d(1000),           # Normalize activations for training stability
            nn.Dropout(0.9),                # Heavy dropout (90%) for regularization
            nn.LeakyReLU(),                 # LeakyReLU activation preserves gradients for negative values
            
            nn.Linear(1000,500),            # Second hidden layer
            nn.BatchNorm1d(500),
            nn.Dropout(0.9),
            nn.LeakyReLU(),
            
            nn.Linear(500,300),             # Third hidden layer  
            nn.BatchNorm1d(300),
            nn.Dropout(0.8),                # Slightly reduced dropout (80%)
            nn.LeakyReLU(),
            
            nn.Linear(300,2),               # Output layer: 2 classes (resistant/susceptible)
        )
        self.temp = temp
        
    def forward(self,x,vimp):
        # Generate adaptive dropout mask based on feature importance
        if self.training:
            unif_noise = torch.rand_like(vimp)
            # unif_noise = torch.full_like(vimp, 0.5)
        else:
            unif_noise = torch.full_like(vimp, 0.5)
        
        # Apply Gumbel-Sigmoid to create differentiable importance weighting
        approx = (
            torch.log(vimp + EPSILON)
            - torch.log(1-vimp + EPSILON)
            + torch.log(unif_noise + EPSILON)
            - torch.log(1. - unif_noise + EPSILON)
        )
        # Apply sigmoid with temperature
        approx_output = torch.sigmoid(approx / self.temp)
        
        # Weight input features by learned importance, then pass through MLP
        out = self.model(x*( approx_output))
        # Apply log softmax for stable classification
        out = F.log_softmax(out, dim=1)
        # loss = F.nll_loss(out, y.long())
        # output = out.max(dim=1).indices
        return out


# Graph Convolutional Neural Network
# Applies Graph Attention Network (GAT) layers to process biological network data
# Selects specific edge types (PPI or Homolog) for each forward pass
class GraphCNN(nn.Module):
    def __init__(self, in_c, hid_c, out_c):
        super(GraphCNN, self).__init__()
        # First GAT layer: applies attention mechanism over graph edges
        self.conv1 = pyg_nn.GATConv(in_channels=in_c, out_channels=hid_c, dropout=0.6 ,heads=1, concat=False)
        # Batch normalization for training stability
        self.bn1   = nn.BatchNorm1d(hid_c)
        # Second GAT layer: produces final classification outputs
        self.conv2 = pyg_nn.GATConv(in_channels=hid_c, out_channels=out_c, dropout=0.6, heads=1, concat=False)
        
    def forward(self, data,edge_type):
        # Extract node features: shape [N, C] (N nodes, C features)
        x = data.x
        # Select specific edge type from data (PPI or Homolog)
        edge_index = data.edge_index[edge_type]
        
        # Apply dropout to input for regularization
        x = F.dropout(x, p=0.6, training=self.training)
        # First GAT layer with attention: learns which edges are important
        hid = self.conv1(x=x, edge_index=edge_index)
        # Batch normalize hidden representations
        hid = self.bn1(hid)
        # Non-linear activation
        hid = F.leaky_relu(hid)
        # Second GAT layer: produces classification logits
        out = self.conv2(x=hid, edge_index=edge_index)
        # Apply log softmax for numerical stability (prevents overflow)
        out = F.log_softmax(out, dim=1)
        
        # Calculate negative log-likelihood loss on training examples
        loss = F.nll_loss(out[data.train_mask],data.y[data.train_mask].long())
        
        return out,loss
    
# Main Model Class
# Combines Multi-GAT (graph neural network) and Variable Dropout MLPs for drug resistance prediction
# Uses ensemble approach: multiple models make independent predictions, then aggregate results
class Model(nn.Module):
    def __init__(self,data_geo_x_shape,num_muti_gat,num_muti_mlp,num_node_features,data_x_N):
        super(Model, self).__init__()
        # Multi-GAT module: processes graph data and learns node importance for drug resistance
        self.mutiGAT = MutiGAT(num_muti_gat=num_muti_gat,num_node_features=num_node_features, hid_c=16, out_c=2,data_x_N=data_x_N)
        # self.vdMLP = VariableDropoutMLP(data_x_shape=data_geo_x_shape)
        
        # Number of MLP modules to ensemble
        self.num_muti_mlp = num_muti_mlp
        # Create multiple Variable Dropout MLPs for diverse predictions
        self.vdMLP_list = []
        for i in range(num_muti_mlp):
            self.vdMLP_list.append(VariableDropoutMLP(data_x_shape=data_geo_x_shape[1]))
        self.vdMLP_list = nn.ModuleList(self.vdMLP_list)
        
    def forward(self,data,data_geo_x):
        # Multi-GAT produces: nodal importance scores, loss, graph-based predictions, adjacency matrix, feature weights
        vimp,loss_mutiGAT,out_graph,graph,pw_w = self.mutiGAT(data)
        
        # Initialize output tensor for accumulating MLP predictions
        out = torch.zeros([data_geo_x.shape[0],2]).to(next(self.parameters()).device)
        
        # Pass genomic features through each MLP with graph-derived importance weights
        for module in self.vdMLP_list:
            # Each MLP makes independent predictions weighted by graph importance
            temp = module(data_geo_x,out_graph)
            out = out + temp.exp()  # Accumulate exponential of log-probabilities
        
        # L1 regularization: penalizes large graph-based predictions (prevents overconfident predictions)
        loss_L1 = torch.mean(torch.pow(out_graph,2))
        
        # Return comprehensive outputs for training and analysis
        return {
            'out':torch.log(out/self.num_muti_mlp),      # Averaged ensemble predictions (log-space)
            'vimp_g':out_graph,                           # Graph-derived importance scores
            'loss_mutiGAT':loss_mutiGAT,                 # Multi-GAT loss for backpropagation
            'loss_L1':loss_L1,                            # L1 regularization loss
            'graph':graph,                                # Learned adjacency matrix
            'temp':temp,                                  # Last MLP output (for debugging)
            'pw_w':pw_w,                                 # Feature importance weights
            'cor':vimp                                    # Node correlations from GAT
        }