import logging
from typing import Dict, List, Optional
import networkx as nx

logger = logging.getLogger(__name__)


def compute_reversal_score(
    drug_name: str,
    gdsc_index: Dict,
    all_candidate_ic50s: Dict[str, Optional[float]]
) -> float:
    """
    Measures drug potency using GDSC IC50 data.
    Lower IC50 = more potent = higher reversal score.

    IMPORTANT: IC50 normalization is across ALL candidates together,
    not per drug in isolation. Pass all_candidate_ic50s from rank_drugs().

    Args:
        drug_name:            the drug to score
        gdsc_index:           full GDSC index
        all_candidate_ic50s:  {drug_name: mean_ic50} for ALL candidates

    Returns:
        float in [0.0, 1.0]. Default 0.5 if IC50 not available.
    """
    drug_key  = drug_name.upper()
    gdsc_entry = gdsc_index.get(drug_key)
    ic50       = gdsc_entry["mean_ic50"] if gdsc_entry else None

    if ic50 is None:
        logger.warning(f"No IC50 for '{drug_name}' — using default 0.5")
        return 0.5

    # Collect all valid IC50 values across candidates
    valid_ic50s = [
        v for v in all_candidate_ic50s.values()
        if v is not None
    ]

    if not valid_ic50s or len(valid_ic50s) == 1:
        return 0.5

    min_ic50 = min(valid_ic50s)
    max_ic50 = max(valid_ic50s)

    if max_ic50 == min_ic50:
        return 0.5

    # Lower IC50 = more potent = higher score
    normalized = (ic50 - min_ic50) / (max_ic50 - min_ic50)
    reversal   = round(1.0 - normalized, 4)

    return reversal


def compute_pathway_coverage(
    drug_name: str,
    dysregulated_pathways: List[str],
    G: nx.Graph
) -> float:
    """
    Fraction of patient's dysregulated pathways this drug covers.

    Formula: len(drug_pathways ∩ dysregulated) / len(dysregulated)

    Returns:
        float in [0.0, 1.0]. 0.0 if no dysregulated pathways.
    """
    if not dysregulated_pathways:
        logger.warning(f"No dysregulated pathways — pathway_coverage=0.0")
        return 0.0

    if drug_name not in G:
        return 0.0

    # Get all pathways this drug is connected to in the graph
    drug_pathways = {
        neighbor
        for neighbor in G.neighbors(drug_name)
        if G.nodes[neighbor].get("type") == "pathway"
    }

    overlap  = drug_pathways.intersection(set(dysregulated_pathways))
    coverage = round(len(overlap) / len(dysregulated_pathways), 4)

    return coverage


def compute_gene_overlap(
    drug_name: str,
    core_genes: List[str],
    G: nx.Graph
) -> float:
    """
    Fraction of patient's core resistance genes this drug directly targets.

    Formula: len(drug_targets ∩ core_genes) / len(core_genes)

    Returns:
        float in [0.0, 1.0]. 0.0 if no core genes.
    """
    if not core_genes:
        logger.warning(f"No core genes — gene_overlap=0.0")
        return 0.0

    if drug_name not in G:
        return 0.0

    # Get all genes this drug targets in the graph
    drug_genes = {
        neighbor
        for neighbor in G.neighbors(drug_name)
        if G.nodes[neighbor].get("type") == "gene"
    }

    overlap = drug_genes.intersection(set(core_genes))
    score   = round(len(overlap) / len(core_genes), 4)

    return score


def compute_sd_score(
    drug_name: str,
    reversal: float,
    pathway_coverage: float,
    gene_overlap: float,
    core_genes: List[str],
    dysregulated_pathways: List[str],
    G: nx.Graph,
    gdsc_index: Dict
) -> Dict:
    """
    Combine component scores into final SD score.
    Adjusts weights automatically when data is missing.

    Standard:          SD = 0.4×R + 0.3×C + 0.3×G
    No core genes:     SD = 0.55×R + 0.45×C
    No pathways:       SD = 0.70×R + 0.30×G

    Returns full score dict including all components and metadata.
    """
    has_genes    = len(core_genes) > 0
    has_pathways = len(dysregulated_pathways) > 0

    # ── Weight selection ──────────────────────────────────────────
    if has_genes and has_pathways:
        sd    = round(0.4 * reversal + 0.3 * pathway_coverage + 0.3 * gene_overlap, 4)
        weights_used = "standard (0.4R + 0.3C + 0.3G)"
    elif not has_genes and has_pathways:
        sd    = round(0.55 * reversal + 0.45 * pathway_coverage, 4)
        weights_used = "no-genes (0.55R + 0.45C)"
    elif has_genes and not has_pathways:
        sd    = round(0.70 * reversal + 0.30 * gene_overlap, 4)
        weights_used = "no-pathways (0.70R + 0.30G)"
    else:
        sd    = round(reversal, 4)
        weights_used = "reversal-only (fallback)"

    # ── Get metadata from graph ───────────────────────────────────
    neighbors     = {}
    targeted_genes     = []
    targeted_pathways  = []

    if drug_name in G:
        for neighbor in G.neighbors(drug_name):
            ntype = G.nodes[neighbor].get("type")
            if ntype == "gene":
                targeted_genes.append(neighbor)
            elif ntype == "pathway":
                targeted_pathways.append(neighbor)

    # ── Get mechanism from graph node ─────────────────────────────
    mechanism = ""
    if drug_name in G:
        mechanism = G.nodes[drug_name].get("mechanism", "")

    # ── Get IC50 ──────────────────────────────────────────────────
    gdsc_entry = gdsc_index.get(drug_name.upper())
    mean_ic50  = gdsc_entry["mean_ic50"] if gdsc_entry else None

    return {
        "drug_name":          drug_name,
        "sd_score":           sd,
        "reversal_score":     reversal,
        "pathway_coverage":   pathway_coverage,
        "gene_overlap":       gene_overlap,
        "weights_used":       weights_used,
        "targeted_genes":     targeted_genes,
        "targeted_pathways":  targeted_pathways,
        "mechanism_of_action": mechanism,
        "mean_ic50_uM":       mean_ic50
    }