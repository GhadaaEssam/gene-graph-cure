from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ModelKey(str, Enum):
    liver = "liver"
    ovarian = "ovarian"
    immunotherapy = "immunotherapy"
    breast = "breast"


class CancerType(str, Enum):
    liver = "liver"
    ovarian = "ovarian"
    immunotherapy = "immunotherapy"
    breast = "breast"


class PredictionRequest(BaseModel):
    geo_features: List[List[float]]
    cancer_type: CancerType


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
    model_config = ConfigDict(extra="allow")

    loss_mutiGAT: Union[float, List[float]]
    loss_L1: Union[float, List[float]]
    out: Optional[Union[List[int], List[List[float]]]] = None
    cor: List[float]
    graph: Optional[List[List[float]]] = None
    graph_shape: Optional[List[int]] = None
    pw_w: List[float]
    vimp_g: List[float]
    temp: List[List[float]]
    structured_core_genes: List[CoreGene] = Field(default_factory=list)
    structured_core_pathways: List[CorePathway] = Field(default_factory=list)
    core_genes: List[str] = Field(default_factory=list)
    core_pathways: List[str] = Field(default_factory=list)
    out_multiomics: Optional[List[List[float]]] = None
    out_multiomics_probabilities: Optional[List[List[float]]] = None
    prediction: Optional[List[int]] = None


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
