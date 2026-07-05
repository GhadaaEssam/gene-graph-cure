from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

class ModelKey(str, Enum):
    liver = "liver"
    ovarian = "ovarian"
    immunotherapy = "immunotherapy"
    colorectal = "colorectal"
    breast = "breast"
    breast_multiomics = "breast_multiomics"

class CoreGene(BaseModel):
    index: int
    name: str
    score: float
    correlation: Optional[float] = None
    is_anchor: bool = False

class CorePathway(BaseModel):
    index: int
    name: str
    weight: float

class PredictionRequest(BaseModel):
    # node_features:  List[List[float]]
    # ppi_edges:      List[List[int]]
    # homolog_edges:  List[List[int]]
    # anchor_genes: List[str]
    geo_features:   List[List[float]]
    cancer_type: CancerType 

class PredictionResult(BaseModel):
    model_config = ConfigDict(extra='allow')

    # Use Union to allow both single numbers and lists of numbers
    loss_mutiGAT: Union[float, List[float]]
    loss_L1: Union[float, List[float]]
    
    # Keeping the others as they were
    out: List[int]
    cor: List[float]
    graph: Optional[List[List[float]]] = None
    graph_shape: Optional[List[int]] = None
    pw_w: List[float]
    vimp_g: List[float]
    temp: List[List[float]]
    out_multiomics: Optional[List[List[float]]] = None
    out_multiomics_probabilities: Optional[List[List[float]]] = None
    prediction: Optional[List[int]] = None

class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
