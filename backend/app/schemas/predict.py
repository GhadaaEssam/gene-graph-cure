from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum

class CancerType(str, Enum):
    lung = "lung"
    breast = "breast"
    colon = "colon"

class PredictionRequest(BaseModel):
    cancer_type: CancerType
    file_reference: str
    metadata: Optional[Dict] = None

class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class PredictionResult(BaseModel):
    resistance_score: float
    core_genes: List[str]
    pathway_scores: Dict[str, float]
    confidence: float