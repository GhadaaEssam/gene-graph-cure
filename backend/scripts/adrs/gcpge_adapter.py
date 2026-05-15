# backend/adrs/gcpge_adapter.py
"""
GC-PGE Output Adapter — Final Version
pw_w has 3090 values, one per pathway in pw_id.csv order.
Each index directly maps to a specific pathway name.
No grouping or aggregation needed.
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Load pathway ID map from pw_id.csv ───────────────────────────
# This file is the same across all cancer types (confirmed by team)
_PW_ID_PATH = Path(__file__).parent / "data" / "pw_id.csv"

def _load_pathway_names() -> List[str]:
    """Load ordered pathway names from pw_id.csv."""
    df = pd.read_csv(_PW_ID_PATH)
    return df["pwid"].tolist()

# Load once at module import — never reload
try:
    PATHWAY_NAMES = _load_pathway_names()
    logger.info(f"Loaded {len(PATHWAY_NAMES)} pathway names from pw_id.csv")
except Exception as e:
    logger.error(f"Failed to load pw_id.csv: {e}")
    PATHWAY_NAMES = [f"pathway_{i}" for i in range(3090)]


def build_delta_e(
    pw_w: List[float],
    top_n: int = 50
) -> Dict[str, float]:
    """
    Convert pw_w list from /predict JSON into named delta_e dict.
    Each pw_w[i] is the rewiring score for PATHWAY_NAMES[i].

    Args:
        pw_w:  list of 3090 floats from gcpge_output["pw_w"]
        top_n: keep only top N pathways by score to reduce noise

    Returns:
        Dict[pathway_name, score] — top_n highest scoring pathways
    """
    if not pw_w:
        logger.warning("pw_w is empty — returning empty delta_e")
        return {}

    weights = np.array(pw_w, dtype=float)

    if len(weights) != len(PATHWAY_NAMES):
        logger.warning(
            f"pw_w length {len(weights)} != "
            f"expected {len(PATHWAY_NAMES)} — mapping by position"
        )

    # Map each weight to its pathway name
    full_delta_e = {
        PATHWAY_NAMES[i]: float(weights[i])
        for i in range(min(len(weights), len(PATHWAY_NAMES)))
    }

    # Keep top_n by score to avoid passing 3090 pathways to scorer
    sorted_pathways = sorted(
        full_delta_e.items(),
        key=lambda x: x[1],
        reverse=True
    )
    delta_e = dict(sorted_pathways[:top_n])

    logger.info(
        f"delta_e built: {len(full_delta_e)} total pathways → "
        f"top {len(delta_e)} kept. "
        f"Top pathway: {sorted_pathways[0][0]} ({sorted_pathways[0][1]:.4f})"
    )
    return delta_e


def build_core_genes(
    vimp_g: List[float],
    anchor_genes: List[str],
    top_n: int = 15,
    threshold: float = 0.0
) -> List[str]:
    """
    Convert vimp_g importance scores into core gene symbol list.

    Args:
        vimp_g:       gene importance scores from gcpge_output["vimp_g"]
        anchor_genes: ordered gene names matching vimp_g positions
                      (from 2_pubmed_result.csv "gene" column in order)
        top_n:        max genes to return (default 15)
        threshold:    min importance score to include (default 0.0 = take all)

    Returns:
        List[str] of gene symbols sorted by importance descending
    """
    if not vimp_g or not anchor_genes:
        logger.warning("vimp_g or anchor_genes empty — returning empty core_genes")
        return []

    paired = list(zip(anchor_genes, [float(v) for v in vimp_g]))
    filtered = [(g, s) for g, s in paired if s >= threshold]
    filtered.sort(key=lambda x: x[1], reverse=True)

    core_genes = [gene for gene, _ in filtered[:top_n]]
    logger.info(f"core_genes: top {len(core_genes)} — {core_genes[:5]}...")
    return core_genes


def translate_gcpge_to_adrs(
    gcpge_response: Dict,
    anchor_genes: List[str],
    patient_id: str,
    resistant_drug: str,
    top_n_drugs: int = 5,
    top_n_pathways: int = 50
) -> Dict:
    """
    Main translation: /predict JSON response → /adrs/recommend request body.

    Args:
        gcpge_response:   full JSON from POST /predict
        anchor_genes:     ordered gene names (same order as vimp_g)
                          = "gene" column of 2_pubmed_result.csv in row order
        patient_id:       patient identifier
        resistant_drug:   drug patient is resistant to
        top_n_drugs:      how many drug recommendations to return
        top_n_pathways:   how many top pathways to pass to ADRS (default 50)

    Returns:
        Dict ready to POST to /api/v1/adrs/recommend
    """
    pw_w   = gcpge_response.get("pw_w",   [])
    vimp_g = gcpge_response.get("vimp_g", [])

    if not pw_w:
        logger.error("pw_w missing from GC-PGE response — cannot build delta_e")
        return {}

    delta_e    = build_delta_e(pw_w, top_n=top_n_pathways)
    core_genes = build_core_genes(vimp_g, anchor_genes)

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
        f"pathways={len(delta_e)} | genes={len(core_genes)}"
    )
    return adrs_request