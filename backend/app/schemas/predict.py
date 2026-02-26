from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum

class CancerType(str, Enum):
    lung = "lung"
    breast = "breast"
    colon = "colon"

class PredictionRequest(BaseModel):
    node_features: List[List[float]]
    ppi_edges: List[List[int]]
    homolog_edges: List[List[int]]
    geo_features: List[float]

class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class PredictionResult(BaseModel):
    prediction: List[List[float]]
    node_importance: List[List[float]]
    graph_matrix: List[List[float]]
    feature_weights: List[List[float]]