from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum

class CancerType(str, Enum):
    lung = "lung"
    breast = "breast"
    colon = "colon"

class PredictionRequest(BaseModel):
    node_features:  List[List[float]]
    ppi_edges:      List[List[int]]
    homolog_edges:  List[List[int]]
    geo_features:   List[List[float]]
    anchor_labels:  Optional[List[int]] = Field(
        default=None,
        description="Optional. 1=resistant, 0=susceptible. "
                    "Used to shape output tensor only. If omitted, all nodes predicted as unknowns."
    )

class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class PredictionResult(BaseModel):
    prediction:       List[List[float]] = Field(..., description="Class probabilities [num_nodes, 2]")
    node_importance:  List[float]       = Field(..., description="Per-node importance scores [num_nodes]")
    graph_matrix:     List[List[float]] = Field(..., description="Learned adjacency matrix [num_nodes, num_nodes]")
    feature_weights:  List[List[float]] = Field(..., description="Pathway importance weights — shape from generalization()")