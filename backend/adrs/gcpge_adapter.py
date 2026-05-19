"""
GC-PGE Output Adapter — (Updated API) Version
====================================================
Translates the live JSON response from POST /predict (port 8000)
into the ADRSRequest format for POST /api/v1/adrs/recommend (port 8001).

Updated to use the new structured fields in the /predict response:
    - core_genes              → List[str]  ready to use directly
    - core_pathways           → List[str]  ready to use directly
    - structured_core_pathways → List[{name, weight}]  used for delta_e
    - structured_core_genes   → List[{name, score}]   used for ranked genes

Old fields (pw_w, vimp_g) are still supported as fallback.
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Pathway ID map (fallback only) ───────────────────────────────
# Used only if structured_core_pathways is absent in the response.
# The model now returns pathway names directly, so this is rarely needed.
_PW_ID_PATH = Path(__file__).parent / "data" / "pw_id.csv"

def _load_pathway_names() -> List[str]:
    df = pd.read_csv(_PW_ID_PATH)
    return df["pwid"].tolist()

try:
    PATHWAY_NAMES = _load_pathway_names()
    logger.info(f"Loaded {len(PATHWAY_NAMES)} pathway names from pw_id.csv")
except Exception as e:
    logger.warning(f"Could not load pw_id.csv ({e}) — fallback disabled")
    PATHWAY_NAMES = []


# ─────────────────────────────────────────────────────────────────
# PRIMARY PATH — uses new structured fields (preferred)
# ─────────────────────────────────────────────────────────────────

def build_delta_e_from_structured(
    structured_core_pathways: List[Dict],
    top_n: int = 50
) -> Dict[str, float]:
    """
    Build delta_e from the new structured_core_pathways field.

    Each entry has: { "index": int, "name": str, "weight": float }

    Args:
        structured_core_pathways: list from gcpge_response["structured_core_pathways"]
        top_n: keep top N pathways by weight

    Returns:
        Dict[pathway_name, weight]
    """
    if not structured_core_pathways:
        return {}

    sorted_pathways = sorted(
        structured_core_pathways,
        key=lambda x: x.get("weight", 0),
        reverse=True
    )

    delta_e = {
        p["name"]: float(p["weight"])
        for p in sorted_pathways[:top_n]
        if p.get("name") and p.get("weight") is not None
    }

    if delta_e:
        top = max(delta_e, key=delta_e.get)
        logger.info(
            f"delta_e from structured_core_pathways: "
            f"{len(delta_e)} pathways. Top: {top} ({delta_e[top]:.4f})"
        )
    return delta_e


def build_core_genes_from_structured(
    structured_core_genes: List[Dict],
    top_n: int = 15
) -> List[str]:
    """
    Build core_genes from the new structured_core_genes field.

    Each entry has: { "index": int, "name": str, "score": float,
                      "correlation": float, "is_anchor": bool }

    Args:
        structured_core_genes: list from gcpge_response["structured_core_genes"]
        top_n: max genes to return

    Returns:
        List[str] of gene names sorted by score descending
    """
    if not structured_core_genes:
        return []

    sorted_genes = sorted(
        structured_core_genes,
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    core_genes = [
        g["name"]
        for g in sorted_genes[:top_n]
        if g.get("name")
    ]

    logger.info(f"core_genes from structured_core_genes: {core_genes[:5]}...")
    return core_genes


# ─────────────────────────────────────────────────────────────────
# FALLBACK PATH — uses raw pw_w / vimp_g (old format)
# ─────────────────────────────────────────────────────────────────

def build_delta_e_from_pw_w(
    pw_w: List[float],
    top_n: int = 50
) -> Dict[str, float]:
    """
    Fallback: build delta_e from raw pw_w vector using pw_id.csv.
    Used when structured_core_pathways is not in the response.
    """
    if not pw_w or not PATHWAY_NAMES:
        logger.warning("pw_w fallback: missing pw_w or PATHWAY_NAMES")
        return {}

    weights = np.array(pw_w, dtype=float)

    full_delta_e = {
        PATHWAY_NAMES[i]: float(weights[i])
        for i in range(min(len(weights), len(PATHWAY_NAMES)))
    }

    sorted_pathways = sorted(
        full_delta_e.items(),
        key=lambda x: x[1],
        reverse=True
    )
    delta_e = dict(sorted_pathways[:top_n])
    logger.info(f"delta_e from pw_w fallback: {len(delta_e)} pathways")
    return delta_e


def build_core_genes_from_vimp_g(
    vimp_g: List[float],
    anchor_genes: List[str],
    top_n: int = 15
) -> List[str]:
    """
    Fallback: build core_genes from raw vimp_g + anchor_genes list.
    Used when structured_core_genes is not in the response.
    """
    if not vimp_g or not anchor_genes:
        logger.warning("vimp_g fallback: missing vimp_g or anchor_genes")
        return []

    paired = list(zip(anchor_genes, [float(v) for v in vimp_g]))
    paired.sort(key=lambda x: x[1], reverse=True)
    core_genes = [gene for gene, _ in paired[:top_n]]
    logger.info(f"core_genes from vimp_g fallback: {core_genes[:5]}...")
    return core_genes


# ─────────────────────────────────────────────────────────────────
# MAIN TRANSLATION FUNCTION
# ─────────────────────────────────────────────────────────────────

def translate_gcpge_to_adrs(
    gcpge_response: Dict,
    patient_id: str,
    resistant_drug: str,
    anchor_genes: Optional[List[str]] = None,
    top_n_drugs: int = 5,
    top_n_pathways: int = 50
) -> Dict:
    """
    Main translation function.
    Converts /predict JSON response → /api/v1/adrs/recommend request body.

    Automatically uses the best available fields:
        1. structured_core_pathways + structured_core_genes  (new — preferred)
        2. core_pathways + core_genes                        (new — simple lists)
        3. pw_w + vimp_g + anchor_genes                      (old — fallback)

    Args:
        gcpge_response:  full JSON dict from POST /predict
        patient_id:      patient identifier (maps to analysis_code in DB)
        resistant_drug:  drug the patient is resistant to
        anchor_genes:    ordered gene name list — only needed for pw_w fallback
        top_n_drugs:     number of drug recommendations to return
        top_n_pathways:  number of top pathways to pass to ADRS

    Returns:
        Dict ready to POST to /api/v1/adrs/recommend
    """

    # ── Build delta_e ─────────────────────────────────────────────
    delta_e = {}

    # Priority 1: structured_core_pathways (new field — name + weight)
    if gcpge_response.get("structured_core_pathways"):
        delta_e = build_delta_e_from_structured(
            gcpge_response["structured_core_pathways"],
            top_n=top_n_pathways
        )
        logger.info("Used structured_core_pathways for delta_e")

    # Priority 2: core_pathways (new field — simple name list, weight=1.0 each)
    elif gcpge_response.get("core_pathways"):
        pathways = gcpge_response["core_pathways"]
        delta_e  = {name: 1.0 for name in pathways[:top_n_pathways]}
        logger.info(
            f"Used core_pathways for delta_e "
            f"({len(delta_e)} pathways, uniform weight)"
        )

    # Priority 3: raw pw_w (old fallback)
    elif gcpge_response.get("pw_w"):
        delta_e = build_delta_e_from_pw_w(
            gcpge_response["pw_w"],
            top_n=top_n_pathways
        )
        logger.warning("Used pw_w fallback for delta_e (old response format)")

    if not delta_e:
        logger.error("Could not build delta_e from response — all fields empty")
        return {}

    # ── Build core_genes ──────────────────────────────────────────
    core_genes = []

    # Priority 1: structured_core_genes (new field — name + score)
    if gcpge_response.get("structured_core_genes"):
        core_genes = build_core_genes_from_structured(
            gcpge_response["structured_core_genes"]
        )
        logger.info("Used structured_core_genes for core_genes")

    # Priority 2: core_genes (new field — simple list)
    elif gcpge_response.get("core_genes"):
        core_genes = gcpge_response["core_genes"][:15]
        logger.info(f"Used core_genes directly: {core_genes[:5]}...")

    # Priority 3: vimp_g + anchor_genes (old fallback)
    elif gcpge_response.get("vimp_g") and anchor_genes:
        core_genes = build_core_genes_from_vimp_g(
            gcpge_response["vimp_g"],
            anchor_genes
        )
        logger.warning("Used vimp_g fallback for core_genes (old response format)")

    # ── Assemble ADRS request ─────────────────────────────────────
    adrs_request = {
        "patient_id":     patient_id,
        "resistant_drug": resistant_drug,
        "delta_e":        delta_e,
        "core_genes":     core_genes,
        "top_n":          top_n_drugs,
        "threshold":      0.5
    }

    logger.info(
        f"ADRS request ready | patient={patient_id} | "
        f"drug={resistant_drug} | "
        f"pathways={len(delta_e)} | genes={len(core_genes)}"
    )
    return adrs_request