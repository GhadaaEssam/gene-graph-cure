from pydantic import BaseModel, ConfigDict, Field
from typing import List, Any, Union, Dict, Optional
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
    anchor_genes: List[str]

class PredictionResult(BaseModel):
    model_config = ConfigDict(extra='allow')

    # Use Union to allow both single numbers and lists of numbers
    loss_mutiGAT: Union[float, List[float]]
    loss_L1: Union[float, List[float]]
    
    # Keeping the others as they were
    out: List[List[float]]
    cor: List[float]
    graph: List[List[float]]
    pw_w: List[float]
    vimp_g: List[float]
    temp: List[List[float]]
    
    # Add this line for the RAG output
    rag_evidence: Optional[List[Dict[str, str]]] = None
        
class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"