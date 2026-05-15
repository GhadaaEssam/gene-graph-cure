"""
ADRS Cache Layer
Saves recommendation results to PostgreSQL and retrieves cached results.
Reduces redundant computation for same patient + resistant drug combinations.
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


def save_recommendations(
    patient_id:      str,
    resistant_drug:  str,
    result:          Dict,
    db_session
) -> bool:
    """
    Save a full ADRS result to PostgreSQL.
    Stores the parent result + one row per recommended drug.

    Args:
        patient_id:     patient identifier
        resistant_drug: drug patient is resistant to
        result:         full dict from rank_drugs() in recommender.py
        db_session:     SQLAlchemy session

    Returns:
        True on success, False on failure
    """
    from app.db.models.adrs_db_tables import AlternativeDrugsResult, DrugRecommendationRecord

    try:
        meta    = result.get("meta", {})
        llm_ctx = result.get("llm_context", {})

        # ── Create parent result row ──────────────────────────────
        result_row = AlternativeDrugsResult(
            patient_id            = patient_id,
            resistant_drug        = resistant_drug,
            timestamp             = datetime.utcnow(),
            threshold_used        = meta.get("threshold_used", 0.5),
            total_candidates      = meta.get("total_candidates", 0),
            dysregulated_pathways = meta.get("dysregulated_pathways", []),
            core_genes            = meta.get("core_genes", []),
            patient_summary       = llm_ctx.get("patient_summary", "") if llm_ctx else "",
            gene_hit_summary      = llm_ctx.get("gene_hit_summary", "") if llm_ctx else "",
            cached                = False
        )
        db_session.add(result_row)
        db_session.flush()   # get result_row.id without full commit

        # ── Create one row per recommended drug ───────────────────
        for rank, drug in enumerate(result.get("recommendations", []), start=1):
            drug_row = DrugRecommendationRecord(
                result_id           = result_row.id,
                rank                = rank,
                drug_name           = drug["drug_name"],
                drug_id             = "",          # DrugBank ID if needed
                sd_score            = drug["sd_score"],
                reversal_score      = drug.get("reversal_score"),
                pathway_coverage    = drug.get("pathway_coverage"),
                gene_overlap        = drug.get("gene_overlap"),
                weights_used        = drug.get("weights_used", ""),
                mean_ic50_uM        = drug.get("mean_ic50_uM"),
                targeted_genes      = drug.get("targeted_genes", []),
                targeted_pathways   = drug.get("targeted_pathways", []),
                mechanism_of_action = drug.get("mechanism_of_action", "")
            )
            db_session.add(drug_row)

        db_session.commit()
        logger.info(
            f"Saved result to DB — patient={patient_id} | "
            f"drug={resistant_drug} | "
            f"recommendations={len(result.get('recommendations', []))}"
        )
        return True

    except Exception as e:
        db_session.rollback()
        logger.error(f"Failed to save recommendations to DB: {e}", exc_info=True)
        return False


def get_cached_result(
    patient_id:     str,
    resistant_drug: str,
    db_session
) -> Optional[Dict]:
    """
    Check if a result already exists in DB for this patient + drug combo.
    Returns the full result dict if found, None if not cached.

    Args:
        patient_id:     patient identifier
        resistant_drug: drug patient is resistant to
        db_session:     SQLAlchemy session

    Returns:
        Dict matching rank_drugs() output format, or None
    """
    from adrs.db_tables import AlternativeDrugsResult, DrugRecommendationRecord

    try:
        # Find most recent result for this patient+drug
        result_row = (
            db_session.query(AlternativeDrugsResult)
            .filter(
                AlternativeDrugsResult.patient_id     == patient_id,
                AlternativeDrugsResult.resistant_drug == resistant_drug
            )
            .order_by(AlternativeDrugsResult.timestamp.desc())
            .first()
        )

        if not result_row:
            return None

        # Reconstruct recommendations list
        drug_rows = (
            db_session.query(DrugRecommendationRecord)
            .filter(DrugRecommendationRecord.result_id == result_row.id)
            .order_by(DrugRecommendationRecord.rank)
            .all()
        )

        recommendations = [
            {
                "drug_name":           row.drug_name,
                "sd_score":            row.sd_score,
                "reversal_score":      row.reversal_score,
                "pathway_coverage":    row.pathway_coverage,
                "gene_overlap":        row.gene_overlap,
                "weights_used":        row.weights_used or "standard (0.4R + 0.3C + 0.3G)",
                "targeted_genes":      row.targeted_genes or [],
                "targeted_pathways":   row.targeted_pathways or [],
                "mechanism_of_action": row.mechanism_of_action or "",
                "mean_ic50_uM":        row.mean_ic50_uM
            }
            for row in drug_rows
        ]

        logger.info(
            f"Cache hit — patient={patient_id} | "
            f"drug={resistant_drug} | "
            f"cached at {result_row.timestamp}"
        )

        return {
            "recommendations": recommendations,
            "meta": {
                "total_candidates":      result_row.total_candidates or 0,
                "dysregulated_pathways": result_row.dysregulated_pathways or [],
                "core_genes":            result_row.core_genes or [],
                "resistant_drug":        result_row.resistant_drug,
                "threshold_used":        result_row.threshold_used or 0.5,
                "top_n":                 len(recommendations)
            },
            "llm_context": {
                "top_3_drugs":          recommendations[:3],
                "patient_summary":      result_row.patient_summary or "",
                "gene_hit_summary":     result_row.gene_hit_summary or "",
                "pathway_explanations": {}
            },
            "cached": True
        }

    except Exception as e:
        logger.error(f"Cache lookup failed: {e}", exc_info=True)
        return None