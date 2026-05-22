from enum import Enum
from typing import Any, List, Optional, Union, Dict

from pydantic import BaseModel, ConfigDict, model_validator


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
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: ModelKey
    geo_features: Any
    include_graph: bool = True

    meth_features: Optional[Any] = None
    cnv_features: Optional[Any] = None
    snv_features: Optional[Any] = None

    @property
    def is_multiomics(self) -> bool:
        return self.model == ModelKey.breast_multiomics

    @property
    def uploaded_files(self) -> dict[str, Any]:
        return {
            "geo_features": self.geo_features,
            "meth_features": self.meth_features,
            "cnv_features": self.cnv_features,
            "snv_features": self.snv_features,
        }

    @model_validator(mode="after")
    def validate_multiomics_files(self):
        optional_omics = {
            "meth_features": self.meth_features,
            "cnv_features": self.cnv_features,
            "snv_features": self.snv_features,
        }

        provided_optional = [
            key for key, value in optional_omics.items()
            if value is not None
        ]

        if self.model == ModelKey.breast_multiomics:

            missing_optional = [
                key for key, value in optional_omics.items()
                if value is None
            ]

            if missing_optional:
                raise ValueError(
                    "breast_multiomics requires all omics files: "
                    f"{', '.join(missing_optional)}"
                )

        elif provided_optional:
            raise ValueError(
                "Optional omics files are only supported "
                "with model=breast_multiomics"
            )

        return self


class PredictionResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    loss_mutiGAT: Union[float, List[float]]
    loss_L1: Union[float, List[float]]

    out: List[int]

    cor: List[float]

    graph: Optional[List[List[float]]] = None
    graph_shape: Optional[List[int]] = None

    pw_w: List[float]
    vimp_g: List[float]

    temp: List[List[float]]

    # multiomics
    out_multiomics: Optional[List[List[float]]] = None
    out_multiomics_probabilities: Optional[List[List[float]]] = None
    prediction: Optional[List[int]] = None

    # rag
    rag_evidence: Optional[List[Dict[str, str]]] = None


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"