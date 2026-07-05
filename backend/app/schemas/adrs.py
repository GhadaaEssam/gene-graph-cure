from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


# ── REQUEST ───────────────────────────────────────────────────────

class ADRSRequest(BaseModel):
    """
    What the frontend / LLM module sends to ADRS endpoint.
    Contains raw GC-PGE output — normalizer handles it internally.
    """
    patient_id:     str            = Field(..., description="Unique patient identifier")
    resistant_drug: str            = Field(..., description="Drug the patient is resistant to")
    delta_e:        Dict[str, float] = Field(..., description="Raw ΔE pathway rewiring scores from GC-PGE")
    core_genes:     List[str]      = Field(..., description="Core resistance genes from GC-PGE")
    top_n:          int            = Field(5,   description="Number of recommendations to return")
    threshold:      float          = Field(0.5, description="ΔE threshold for dysregulation")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id":     "patient_001",
                "resistant_drug": "Erlotinib",
                "delta_e": {
                    "EGFR signaling":     0.82,
                    "PI3K/MTOR signaling": 0.61,
                    "ERK MAPK signaling": 0.45,
                    "Cell cycle":         0.30,
                    "Apoptosis regulation": 0.20
                },
                "core_genes": ["EGFR", "KRAS", "TP53", "PIK3CA"],
                "top_n":      5,
                "threshold":  0.5
            }
        }


# ── RESPONSE COMPONENTS ───────────────────────────────────────────

class DrugRecommendation(BaseModel):
    """Single drug recommendation with full score breakdown."""
    drug_name:           str
    sd_score:            float
    reversal_score:      float
    pathway_coverage:    float
    gene_overlap:        float
    weights_used:        str
    targeted_genes:      List[str]
    targeted_pathways:   List[str]
    mechanism_of_action: str
    mean_ic50_uM:        Optional[float] = None


class LLMContextPacket(BaseModel):
    """
    Structured context for the LLM explanation module.
    Contains top 3 drugs and patient summary.
    """
    top_3_drugs:          List[DrugRecommendation]
    patient_summary:      str
    gene_hit_summary:     str
    pathway_explanations: Dict[str, str]


class ResponseMeta(BaseModel):
    """Pipeline metadata — useful for debugging."""
    total_candidates:      int
    dysregulated_pathways: List[str]
    core_genes:            List[str]
    resistant_drug:        str
    threshold_used:        float
    top_n:                 int


# ── MAIN RESPONSE ─────────────────────────────────────────────────

class ADRSResponse(BaseModel):
    """
    Full response returned by POST /api/v1/adrs/recommend
    """
    patient_id:      str
    resistant_drug:  str
    recommendations: List[DrugRecommendation]
    llm_context:     Optional[LLMContextPacket] = None
    meta:            Optional[ResponseMeta]     = None
    timestamp:       datetime                   = Field(default_factory=datetime.utcnow)
    cached:          bool                       = False

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id":     "patient_001",
                "resistant_drug": "Erlotinib",
                "recommendations": [
                    {
                        "drug_name":        "Osimertinib",
                        "sd_score":          0.6135,
                        "reversal_score":    0.9712,
                        "pathway_coverage":  0.5,
                        "gene_overlap":      0.25,
                        "weights_used":      "standard (0.4R + 0.3C + 0.3G)",
                        "targeted_genes":    ["EGFR"],
                        "targeted_pathways": ["EGFR signaling"],
                        "mechanism_of_action": "Osimertinib inhibits EGFR...",
                        "mean_ic50_uM":      0.0123
                    }
                ],
                "cached":    False,
                "timestamp": "2026-04-06T07:00:00"
            }
        }


# ── ERROR RESPONSE ────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Returned when ADRS cannot compute recommendations."""
    error: str
    code:  str

    class Config:
        json_schema_extra = {
            "examples": {
                "no_pathway_match": {
                    "error": "No suitable alternative drugs found.",
                    "code":  "NO_PATHWAY_MATCH"
                },
                "db_unavailable": {
                    "error": "Model cannot compute recommendations.",
                    "code":  "DB_UNAVAILABLE"
                }
            }
        }