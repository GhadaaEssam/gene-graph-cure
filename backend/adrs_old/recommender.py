import logging
from typing import Dict, List, Optional
import networkx as nx

from backend.adrs_old.normalizer import normalize_delta_e
from backend.adrs_old.pathway_mapper import get_standard_pathways
from backend.adrs_old.graph_builder import query_candidates
from backend.adrs_old.scoring import (
    compute_reversal_score,
    compute_pathway_coverage,
    compute_gene_overlap,
    compute_sd_score
)
from backend.adrs_old.db_parser import query_dgidb

logger = logging.getLogger(__name__)


def build_llm_context(
    recommendations: List[Dict],
    core_genes: List[str],
    dysregulated_pathways: List[str],
    resistant_drug: str
) -> Dict:
    """
    Build structured context packet for LLM teammate.
    Contains top 3 drugs with explanations.
    """
    top3 = recommendations[:3]

    gene_summaries = []
    for drug in top3:
        hits = [g for g in drug["targeted_genes"] if g in core_genes]
        if hits:
            gene_summaries.append(
                f"{drug['drug_name']} targets {len(hits)} resistance "
                f"gene(s): {', '.join(hits)}"
            )

    return {
        "top_3_drugs": top3,
        "patient_summary": (
            f"Patient resistant to {resistant_drug}. "
            f"Core resistance genes: {', '.join(core_genes)}. "
            f"Top rewired pathways: {', '.join(dysregulated_pathways[:2])}."
        ),
        "gene_hit_summary": " | ".join(gene_summaries) if gene_summaries
                            else "No direct gene hits in top recommendations.",
        "pathway_explanations": {
            p: f"Pathway '{p}' is highly rewired (above ΔE threshold) "
               f"in this patient's resistance profile."
            for p in dysregulated_pathways
        }
    }


def rank_drugs(
    G: nx.Graph,
    gdsc_index: Dict,
    delta_e: Dict[str, float],
    core_genes: List[str],
    resistant_drug: str,
    top_n: int = 5,
    threshold: float = 0.5
) -> Dict:
    """
    Main ADRS pipeline. Takes raw GC-PGE output, returns ranked drugs.

    Pipeline order:
        1. normalize_delta_e
        2. get_standard_pathways
        3. query_candidates (from graph)
        4. DGIdb fallback (for genes with no candidates)
        5. score all candidates
        6. rank and return top_n
        7. build LLM context packet

    Args:
        G:              knowledge graph from graph_builder
        gdsc_index:     GDSC IC50 index
        delta_e:        raw ΔE from GC-PGE (NOT normalized yet)
        core_genes:     resistance genes from GC-PGE
        resistant_drug: drug patient is already resistant to
        top_n:          number of recommendations to return
        threshold:      ΔE threshold for dysregulation (default 0.5)

    Returns:
        {
            "recommendations": [...],
            "llm_context": {...},
            "meta": {...}
        }
    """

    # ── STEP 1: Normalize ΔE ─────────────────────────────────────
    delta_e_norm = normalize_delta_e(delta_e)

    if not delta_e_norm:
        return _error_response("EMPTY_DELTA_E", "No pathway rewiring data provided.")

    # ── STEP 2: Extract dysregulated pathways ─────────────────────
    dysregulated_pathways = get_standard_pathways(delta_e_norm, threshold)

    if not dysregulated_pathways and not core_genes:
        return _error_response(
            "NO_PATHWAY_MATCH",
            "No suitable alternative drugs found."
        )

    # ── STEP 3: Get candidates from graph ─────────────────────────
    candidates = query_candidates(G, core_genes, dysregulated_pathways, resistant_drug)

    # ── STEP 4: DGIdb fallback for genes with no graph hits ───────
    genes_in_graph = {
        n for n in G.nodes()
        if G.nodes[n].get("type") == "gene"
    }

    for gene in core_genes:
        if gene not in genes_in_graph:
            logger.warning(f"Gene '{gene}' not in graph — querying DGIdb fallback")
            dgidb_drugs = query_dgidb(gene)
            for drug_name in dgidb_drugs:
                if (
                    drug_name not in candidates
                    and drug_name.upper() != resistant_drug.upper()
                ):
                    candidates.append(drug_name)

    if len(candidates) < 3:
        logger.warning(f"Only {len(candidates)} candidates found — below minimum of 3")
        if len(candidates) == 0:
            return _error_response(
                "INSUFFICIENT_CANDIDATES",
                "Not enough candidate drugs found for this resistance profile."
            )

    logger.info(f"Total candidates to score: {len(candidates)}")

    # ── STEP 5: Build IC50 lookup for ALL candidates together ─────
    # Must be done before scoring — normalization needs all values
    all_ic50s = {}
    for drug in candidates:
        entry = gdsc_index.get(drug.upper())
        all_ic50s[drug] = entry["mean_ic50"] if entry else None

    # ── STEP 6: Score all candidates ─────────────────────────────
    scored = []
    for drug_name in candidates:
        reversal = compute_reversal_score(drug_name, gdsc_index, all_ic50s)
        coverage = compute_pathway_coverage(drug_name, dysregulated_pathways, G)
        overlap  = compute_gene_overlap(drug_name, core_genes, G)
        result   = compute_sd_score(
            drug_name, reversal, coverage, overlap,
            core_genes, dysregulated_pathways, G, gdsc_index
        )
        scored.append(result)

    # ── STEP 7: Sort and return top N ────────────────────────────
    scored.sort(key=lambda x: x["sd_score"], reverse=True)
    top_drugs = scored[:top_n]

    # ── STEP 8: Build LLM context packet ─────────────────────────
    llm_context = build_llm_context(
        top_drugs, core_genes, dysregulated_pathways, resistant_drug
    )

    logger.info(
        f"Top {top_n} recommendations: "
        f"{[d['drug_name'] + '=' + str(d['sd_score']) for d in top_drugs]}"
    )

    return {
        "recommendations": top_drugs,
        "llm_context":     llm_context,
        "meta": {
            "total_candidates":     len(candidates),
            "dysregulated_pathways": dysregulated_pathways,
            "core_genes":           core_genes,
            "resistant_drug":       resistant_drug,
            "threshold_used":       threshold,
            "top_n":                top_n
        }
    }


def _error_response(code: str, message: str) -> Dict:
    """Standard error response format."""
    logger.error(f"ADRS error [{code}]: {message}")
    return {
        "error":           message,
        "code":            code,
        "recommendations": [],
        "llm_context":     None,
        "meta":            {}
    }