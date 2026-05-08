from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Union
from enum import Enum

class CancerType(str, Enum):
    lung = "lung"
    breast = "breast"
    colon = "colon"

class ModelKey(str, Enum):
    liver = "liver"
    ovarian = "ovarian"
    immunotherapy = "immunotherapy"

class PredictionRequest(BaseModel):
    node_features:  List[List[float]]
    ppi_edges:      List[List[int]]
    homolog_edges:  List[List[int]]
    geo_features:   List[List[float]]
    anchor_genes: List[str]

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

class PredictionResult(BaseModel):
    model_config = ConfigDict(extra='allow')

    # Use Union to allow both single numbers and lists of numbers
    loss_mutiGAT: Union[float, List[float]]
    loss_L1: Union[float, List[float]]
    
    # Keeping the others as they were
    out: List[int]
    cor: List[float]
    graph: List[List[float]]
    pw_w: List[float]
    vimp_g: List[float]
    temp: List[List[float]]
    structured_core_genes: List[CoreGene] = Field(default_factory=list)
    structured_core_pathways: List[CorePathway] = Field(default_factory=list)
    core_genes: List[str] = Field(default_factory=list)
    core_pathways: List[str] = Field(default_factory=list)
        
class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
