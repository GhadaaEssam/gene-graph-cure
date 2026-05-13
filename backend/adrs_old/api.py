import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from backend.adrs_old.models import (
    ADRSRequest, ADRSResponse,
    ResponseMeta, LLMContextPacket, DrugRecommendation
)
from backend.adrs_old.recommender import rank_drugs

logger = logging.getLogger(__name__)

# ── DB session factory ────────────────────────────────────────────
# Set by main.py at startup if PostgreSQL is available.
# If None, the API runs without caching — all features still work.
_SessionFactory = None

router = APIRouter(prefix="/adrs", tags=["ADRS"])


@router.post(
    "/recommend",
    response_model=ADRSResponse,
    summary="Get alternative drug recommendations",
    description=(
        "Accepts GC-PGE output (delta_e + core_genes) and returns "
        "top-N ranked alternative drugs with SD scores. "
        "Results are cached in PostgreSQL — same patient+drug returns instantly on second call."
    )
)
async def recommend(request: Request, body: ADRSRequest):
    """
    Main ADRS endpoint. Full pipeline:
        1. Check DB cache (return immediately if already computed)
        2. Validate app state (graph loaded)
        3. Run rank_drugs pipeline
        4. Save result to DB cache
        5. Return ADRSResponse
    """

    # ── STEP 1: Check cache ───────────────────────────────────────
    if _SessionFactory is not None:
        try:
            from backend.adrs_old.cache import get_cached_result
            with _SessionFactory() as session:
                cached = get_cached_result(
                    body.patient_id,
                    body.resistant_drug,
                    session
                )
            if cached:
                logger.info(
                    f"Cache hit | "
                    f"patient={body.patient_id} | "
                    f"drug={body.resistant_drug}"
                )
                return _build_response(body, cached, is_cached=True)
        except Exception as e:
            logger.warning(f"Cache check failed — continuing without cache: {e}")

    # ── STEP 2: Validate app state ────────────────────────────────
    if not hasattr(request.app.state, "graph"):
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Model cannot compute recommendations.",
                "code":  "DB_UNAVAILABLE"
            }
        )

    G          = request.app.state.graph
    gdsc_index = request.app.state.gdsc_index

    logger.info(
        f"ADRS request | "
        f"patient={body.patient_id} | "
        f"resistant_drug={body.resistant_drug} | "
        f"genes={body.core_genes} | "
        f"pathways_received={len(body.delta_e)}"
    )

    # ── STEP 3: Run pipeline ──────────────────────────────────────
    try:
        result = rank_drugs(
            G              = G,
            gdsc_index     = gdsc_index,
            delta_e        = body.delta_e,
            core_genes     = body.core_genes,
            resistant_drug = body.resistant_drug,
            top_n          = body.top_n,
            threshold      = body.threshold
        )
    except Exception as e:
        logger.error(f"Unexpected error in rank_drugs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={
            "error": "Internal error during drug recommendation.",
            "code":  "INTERNAL_ERROR"
        })

    # ── Handle pipeline error responses ──────────────────────────
    if "error" in result and not result["recommendations"]:
        raise HTTPException(status_code=422, detail={
            "error": result["error"],
            "code":  result["code"]
        })

    # ── STEP 4: Save to DB cache ──────────────────────────────────
    if _SessionFactory is not None:
        try:
            from backend.adrs_old.cache import save_recommendations
            with _SessionFactory() as session:
                save_recommendations(
                    body.patient_id,
                    body.resistant_drug,
                    result,
                    session
                )
        except Exception as e:
            logger.warning(f"Cache save failed — result still returned: {e}")

    # ── STEP 5: Build and return response ─────────────────────────
    response = _build_response(body, result, is_cached=False)

    # ── Log top 5 drugs to terminal ───────────────────────────────
    recs = response.recommendations
    if recs:
        logger.info(
            f"ADRS response | "
            f"patient={body.patient_id} | "
            f"resistant_to={body.resistant_drug}"
        )
        logger.info(f"  {'#':<4}{'Drug':<26}{'SD':>7}{'R':>7}{'C':>7}{'G':>7}")
        logger.info(f"  {'-'*54}")
        for i, drug in enumerate(recs[:5], 1):
            logger.info(
                f"  {i:<4}{drug.drug_name:<26}"
                f"{drug.sd_score:>7.4f}"
                f"{drug.reversal_score:>7.4f}"
                f"{drug.pathway_coverage:>7.4f}"
                f"{drug.gene_overlap:>7.4f}"
            )

    return response


def _build_response(
    body: ADRSRequest,
    result: dict,
    is_cached: bool
) -> ADRSResponse:
    """
    Internal helper: convert rank_drugs() result dict into ADRSResponse.
    Used by both fresh results and cached results.
    """
    recommendations = [
        DrugRecommendation(**drug)
        for drug in result["recommendations"]
    ]

    llm_context = None
    if result.get("llm_context"):
        ctx = result["llm_context"]
        top3 = []
        for d in ctx.get("top_3_drugs", []):
            if isinstance(d, dict):
                top3.append(DrugRecommendation(**d))
            else:
                top3.append(d)

        llm_context = LLMContextPacket(
            top_3_drugs          = top3,
            patient_summary      = ctx.get("patient_summary", ""),
            gene_hit_summary     = ctx.get("gene_hit_summary", ""),
            pathway_explanations = ctx.get("pathway_explanations", {})
        )

    meta = None
    if result.get("meta"):
        meta = ResponseMeta(**result["meta"])

    return ADRSResponse(
        patient_id      = body.patient_id,
        resistant_drug  = body.resistant_drug,
        recommendations = recommendations,
        llm_context     = llm_context,
        meta            = meta,
        timestamp       = datetime.utcnow(),
        cached          = is_cached
    )


@router.get(
    "/health",
    summary="Health check",
    description=(
        "Verify ADRS module is loaded and ready. "
        "Call this before /recommend to confirm the graph is in memory."
    )
)
async def health(request: Request):
    """Returns status, graph size, and DB cache status."""
    if not hasattr(request.app.state, "graph"):
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "reason": "Graph not loaded"}
        )

    G          = request.app.state.graph
    drug_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "drug"]
    pw_nodes   = [n for n, d in G.nodes(data=True) if d.get("type") == "pathway"]
    gene_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "gene"]

    return {
        "status":           "ok",
        "port":             8001,
        "drugs_loaded":     len(drug_nodes),
        "genes_loaded":     len(gene_nodes),
        "pathways_loaded":  len(pw_nodes),
        "graph_nodes":      G.number_of_nodes(),
        "graph_edges":      G.number_of_edges(),
        "db_cache":         "connected" if _SessionFactory else "disconnected"
    }