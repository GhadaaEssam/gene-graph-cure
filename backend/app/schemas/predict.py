from pydantic import BaseModel, ConfigDict, Field
from typing import List, Any, Union, Optional
from enum import Enum

class ModelKey(str, Enum):
    liver = "liver"
    ovarian = "ovarian"
    immunotherapy = "immunotherapy"
    colorectal = "colorectal"
    breast = "breast"

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
