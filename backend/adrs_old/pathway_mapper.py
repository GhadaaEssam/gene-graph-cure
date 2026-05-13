import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# ── Pathway name translation dictionary ───────────────────────────
# GC-PGE output names → DrugBank/GDSC pathway names
# Add more mappings here as you discover mismatches during testing
PATHWAY_NAME_MAP = {
    # ── Short names (existing mappings) ───────────────────────────
    "EGFR_signaling":          "EGFR signaling",
    "EGFR signaling pathway":  "EGFR signaling",
    "ErbB signaling pathway":  "EGFR signaling",
    "erbb_signaling":          "EGFR signaling",
    "PI3K_AKT_mTOR":           "PI3K/MTOR signaling",
    "PI3K_AKT":                "PI3K/MTOR signaling",
    "PI3K/AKT/mTOR":           "PI3K/MTOR signaling",
    "pi3k_mtor":               "PI3K/MTOR signaling",
    "PI3K/MTOR signaling":     "PI3K/MTOR signaling",
    "MAPK_ERK":                "ERK MAPK signaling",
    "MAPK":                    "ERK MAPK signaling",
    "RAS_MAPK":                "ERK MAPK signaling",
    "ERK MAPK signaling":      "ERK MAPK signaling",
    "mapk_signaling":          "ERK MAPK signaling",
    "Apoptosis":               "Apoptosis regulation",
    "apoptosis_pathway":       "Apoptosis regulation",
    "Apoptosis regulation":    "Apoptosis regulation",
    "Cell_cycle_regulation":   "Cell cycle",
    "cell_cycle":              "Cell cycle",
    "Cell cycle":              "Cell cycle",
    "WNT_signaling":           "WNT signaling",
    "Wnt_pathway":             "WNT signaling",
    "WNT signaling":           "WNT signaling",
    "ABL_signaling":           "ABL signaling",
    "ABL signaling":           "ABL signaling",
    "RTK_signaling":           "RTK signaling",
    "RTK signaling":           "RTK signaling",
    "DNA_damage_response":     "Genome integrity",
    "Genome integrity":        "Genome integrity",
    "DNA replication":         "DNA replication",
    "chromatin_remodeling":    "Chromatin histone acetylation",
    "Chromatin histone acetylation": "Chromatin histone acetylation",
    "protein_degradation":     "Protein stability and degradation",
    "Protein stability and degradation": "Protein stability and degradation",

    # ── BIOCARTA pathways → GDSC categories ───────────────────────
    "BIOCARTA_EGFR_SMRTE_PATHWAY":       "EGFR signaling",
    "BIOCARTA_EGF_PATHWAY":              "EGFR signaling",
    "BIOCARTA_ERBB2_PATHWAY":            "EGFR signaling",
    "BIOCARTA_ERBB_PATHWAY":             "EGFR signaling",
    "BIOCARTA_PI3K_PATHWAY":             "PI3K/MTOR signaling",
    "BIOCARTA_AKT_PATHWAY":              "PI3K/MTOR signaling",
    "BIOCARTA_MTOR_PATHWAY":             "PI3K/MTOR signaling",
    "BIOCARTA_MAPK_PATHWAY":             "ERK MAPK signaling",
    "BIOCARTA_ERK_PATHWAY":              "ERK MAPK signaling",
    "BIOCARTA_RAS_PATHWAY":              "ERK MAPK signaling",
    "BIOCARTA_MEK_PATHWAY":              "ERK MAPK signaling",
    "BIOCARTA_APOPTOSIS_PATHWAY":        "Apoptosis regulation",
    "BIOCARTA_BCL2_PATHWAY":             "Apoptosis regulation",
    "BIOCARTA_CASPASE_PATHWAY":          "Apoptosis regulation",
    "BIOCARTA_CELL_CYCLE_PATHWAY":       "Cell cycle",
    "BIOCARTA_CDK_PATHWAY":              "Cell cycle",
    "BIOCARTA_G1_PATHWAY":               "Cell cycle",
    "BIOCARTA_WNT_PATHWAY":              "WNT signaling",
    "BIOCARTA_WNT_BETA_CATENIN_PATHWAY": "WNT signaling",
    "BIOCARTA_ABL_PATHWAY":              "ABL signaling",
    "BIOCARTA_BCR_PATHWAY":              "ABL signaling",
    "BIOCARTA_VEGF_PATHWAY":             "RTK signaling",
    "BIOCARTA_MET_PATHWAY":              "RTK signaling",
    "BIOCARTA_PDGF_PATHWAY":             "RTK signaling",
    "BIOCARTA_IGF_PATHWAY":              "RTK signaling",
    "BIOCARTA_FGFR_PATHWAY":             "RTK signaling",
    "BIOCARTA_DNA_REPAIR_PATHWAY":       "Genome integrity",
    "BIOCARTA_ATM_PATHWAY":              "Genome integrity",
    "BIOCARTA_P53_PATHWAY":              "Genome integrity",
    "BIOCARTA_TELOMERE_PATHWAY":         "Genome integrity",
    "BIOCARTA_HDAC_PATHWAY":             "Chromatin histone acetylation",
    "BIOCARTA_PROTEASOME_PATHWAY":       "Protein stability and degradation",
    "BIOCARTA_UBIQUITIN_PATHWAY":        "Protein stability and degradation",

    # ── REACTOME pathways → GDSC categories ───────────────────────
    "REACTOME_SIGNALING_BY_EGFR":                        "EGFR signaling",
    "REACTOME_EGFR_DOWNREGULATION":                      "EGFR signaling",
    "REACTOME_GAB1_SIGNALOSOME":                         "EGFR signaling",
    "REACTOME_SIGNALING_BY_ERBB2":                       "EGFR signaling",
    "REACTOME_CONSTITUTIVE_SIGNALING_BY_LIGAND_RESPONSIVE_EGFR": "EGFR signaling",
    "REACTOME_PI3K_AKT_SIGNALING":                       "PI3K/MTOR signaling",
    "REACTOME_MTORC1_MEDIATED_SIGNALLING":               "PI3K/MTOR signaling",
    "REACTOME_MTORC2_MEDIATED_SIGNALLING":               "PI3K/MTOR signaling",
    "REACTOME_PTEN_REGULATION":                          "PI3K/MTOR signaling",
    "REACTOME_MAPK1_ERK2_ACTIVATION":                    "ERK MAPK signaling",
    "REACTOME_MAPK3_ERK1_ACTIVATION":                    "ERK MAPK signaling",
    "REACTOME_RAF_MAP_KINASE_CASCADE":                   "ERK MAPK signaling",
    "REACTOME_RAS_SIGNALING":                            "ERK MAPK signaling",
    "REACTOME_MAPK_FAMILY_SIGNALING_CASCADES":           "ERK MAPK signaling",
    "REACTOME_INTRINSIC_PATHWAY_FOR_APOPTOSIS":          "Apoptosis regulation",
    "REACTOME_EXTRINSIC_PATHWAY_FOR_APOPTOSIS":          "Apoptosis regulation",
    "REACTOME_APOPTOSIS":                                "Apoptosis regulation",
    "REACTOME_BCL2_FAMILY_EVENTS":                       "Apoptosis regulation",
    "REACTOME_CELL_CYCLE":                               "Cell cycle",
    "REACTOME_CELL_CYCLE_CHECKPOINTS":                   "Cell cycle",
    "REACTOME_G1_S_TRANSITION":                          "Cell cycle",
    "REACTOME_G2_M_CHECKPOINTS":                         "Cell cycle",
    "REACTOME_MITOTIC_CELL_CYCLE":                       "Cell cycle",
    "REACTOME_SIGNALING_BY_WNT":                         "WNT signaling",
    "REACTOME_TCF_DEPENDENT_SIGNALING_IN_RESPONSE_TO_WNT": "WNT signaling",
    "REACTOME_BCR_SIGNALING":                            "ABL signaling",
    "REACTOME_SIGNALING_BY_ABL":                         "ABL signaling",
    "REACTOME_VEGFA_VEGFR2_PATHWAY":                     "RTK signaling",
    "REACTOME_SIGNALING_BY_MET":                         "RTK signaling",
    "REACTOME_SIGNALING_BY_PDGF":                        "RTK signaling",
    "REACTOME_SIGNALING_BY_FGFR":                        "RTK signaling",
    "REACTOME_DNA_REPAIR":                               "Genome integrity",
    "REACTOME_DNA_DAMAGE_RESPONSE":                      "Genome integrity",
    "REACTOME_TP53_REGULATION":                          "Genome integrity",
    "REACTOME_TELOMERE_MAINTENANCE":                     "Genome integrity",
    "REACTOME_DNA_REPLICATION":                          "DNA replication",
    "REACTOME_SYNTHESIS_OF_DNA":                         "DNA replication",
    "REACTOME_HDAC_DEACETYLATES_HISTONES":               "Chromatin histone acetylation",
    "REACTOME_HAT1_ACETYLATES_HISTONES":                 "Chromatin histone acetylation",
    "REACTOME_PROTEIN_UBIQUITINATION":                   "Protein stability and degradation",
    "REACTOME_PROTEASOMAL_PROTEIN_CATABOLIC_PROCESS":    "Protein stability and degradation",

    # ── PID pathways → GDSC categories ───────────────────────────
    "PID_ERBB_NETWORK_PATHWAY":          "EGFR signaling",
    "PID_EGF_PATHWAY":                   "EGFR signaling",
    "PID_PI3KCI_AKT_PATHWAY":            "PI3K/MTOR signaling",
    "PID_MTOR_4PATHWAY":                 "PI3K/MTOR signaling",
    "PID_RAS_PATHWAY":                   "ERK MAPK signaling",
    "PID_MAPK_TRK_PATHWAY":              "ERK MAPK signaling",
    "PID_WNT_SIGNALING_PATHWAY":         "WNT signaling",
    "PID_APOPTOSIS_PATHWAY":             "Apoptosis regulation",

    # ── SA pathways → GDSC categories ────────────────────────────
    "SA_TRKA_RECEPTOR":                  "RTK signaling",
    "SA_TRKB_RECEPTOR":                  "RTK signaling",
    "SA_TRKC_RECEPTOR":                  "RTK signaling",
    "SA_G1_AND_S_PHASES":                "Cell cycle",
    "SA_PTEN_PATHWAY":                   "PI3K/MTOR signaling",
}


def extract_dysregulated_pathways(
    delta_e_normalized: Dict[str, float],
    threshold: float = 0.5
) -> List[str]:
    """
    Filter normalized ΔE dict to pathways above threshold.
    Input must already be normalized to [0, 1] by normalizer.py.

    Args:
        delta_e_normalized: output of normalize_delta_e()
        threshold: keep pathways with score >= this value (default 0.5)

    Returns:
        List of pathway names with high rewiring scores
    """
    if not delta_e_normalized:
        logger.warning("extract_dysregulated_pathways received empty delta_e")
        return []

    dysregulated = [
        pathway
        for pathway, score in delta_e_normalized.items()
        if score >= threshold
    ]

    logger.info(
        f"Dysregulated pathways (threshold={threshold}): "
        f"{len(dysregulated)} of {len(delta_e_normalized)} — {dysregulated}"
    )
    return dysregulated


def map_to_standard_names(pathway_names: List[str]) -> List[str]:
    """
    Translate GC-PGE pathway names to standard names used in DrugBank/GDSC.
    Unknown names are kept as-is (they may still match directly).

    Args:
        pathway_names: raw pathway names from GC-PGE output

    Returns:
        List of standardized pathway names
    """
    standardized = []
    for name in pathway_names:
        mapped = PATHWAY_NAME_MAP.get(name)
        if mapped:
            standardized.append(mapped)
            if mapped != name:
                logger.info(f"Pathway mapped: '{name}' → '{mapped}'")
        else:
            # Keep original — may still match directly in DrugBank/GDSC
            standardized.append(name)
            logger.warning(f"No mapping found for pathway '{name}' — keeping as-is")

    # Deduplicate while preserving order
    seen = set()
    result = []
    for p in standardized:
        if p not in seen:
            seen.add(p)
            result.append(p)

    return result


def get_standard_pathways(
    delta_e_normalized: Dict[str, float],
    threshold: float = 0.5
) -> List[str]:
    """
    Combined convenience function: extract + translate in one call.
    This is what recommender.py calls.

    Args:
        delta_e_normalized: output of normalize_delta_e()
        threshold: dysregulation threshold

    Returns:
        List of standard pathway names ready for graph querying
    """
    dysregulated = extract_dysregulated_pathways(delta_e_normalized, threshold)
    standardized = map_to_standard_names(dysregulated)
    return standardized