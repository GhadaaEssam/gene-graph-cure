from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from sqlalchemy.orm import Session
import uuid
from typing import Optional
from pathlib import Path
import logging

from app.services.model_service_registry import ModelServiceRegistry
from app.schemas.adrs import ADRSRequest
from app.services.adrs_service import ADRSService, ADRSServiceError
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.db.models.user import User
from app.db.models.prediction_history import PredictionHistory
from app.db.models.prediction_details import PredictionDetails

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Analysis"])

# -------------------- MODEL REGISTRY --------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
WEIGHTS_DIR = PROJECT_ROOT / "weights"
MODEL_INPUTS_DIR = PROJECT_ROOT / "model_inputs"

MODEL_FILES = {
    "liver": "liver_model.pt",
    "ovarian": "ovarian_model.pt",
    "immunotherapy": "immunotherapy_model.pt",
    "breast": "breast_model.pt",
    "colorectal": "colorectal_model.pt",
    "breast_multiomics": "final_multiomics_model.pt",
}

model_registry = ModelServiceRegistry(
    weights_dir=WEIGHTS_DIR,
    model_inputs_dir=MODEL_INPUTS_DIR,
    model_files=MODEL_FILES,
)


def _shape(value):
    if not isinstance(value, list):
        return None

    rows = len(value)
    if rows and isinstance(value[0], list):
        return [rows, len(value[0])]
    return [rows]


def _sample(value, limit=10):
    if isinstance(value, list):
        return value[:limit]
    return value


def _alignment_log_summary(report):
    if not isinstance(report, dict):
        return None

    summary = {
        key: report.get(key)
        for key in (
            "orientation",
            "gene_axis_name",
            "expected_genes",
            "uploaded_genes",
            "matched_genes",
            "missing_genes",
            "extra_genes",
            "sample_count",
            "match_rate",
            "fill_strategy",
            "min_match_rate",
            "identifier_aliases",
        )
        if key in report
    }

    for key in ("matched_gene_names", "missing_gene_names", "extra_gene_names"):
        names = report.get(key)
        if isinstance(names, list):
            summary[f"{key}_count"] = len(names)
            summary[f"{key}_sample"] = names[:5]

    duplicate_genes = report.get("duplicate_genes")
    if isinstance(duplicate_genes, dict):
        summary["duplicate_gene_count"] = len(duplicate_genes)
        summary["duplicate_gene_sample"] = dict(list(duplicate_genes.items())[:5])

    return summary


def _model_result_log_summary(result):
    return {
        "keys": sorted(result.keys()),
        "out_shape": _shape(result.get("out")),
        "out_sample": _sample(result.get("out")),
        "out_probabilities_shape": _shape(result.get("out_probabilities")),
        "out_multiomics_probabilities_shape": _shape(
            result.get("out_multiomics_probabilities")
        ),
        "graph_shape": result.get("graph_shape") or _shape(result.get("graph")),
        "vimp_g_shape": _shape(result.get("vimp_g")),
        "pw_w_shape": _shape(result.get("pw_w")),
        "cor_shape": _shape(result.get("cor")),
        "top_genes": [
            gene.get("name")
            for gene in result.get("structured_core_genes", [])[:5]
        ],
        "top_pathways": [
            pathway.get("name")
            for pathway in result.get("structured_core_pathways", [])[:5]
        ],
        "input_alignment": _alignment_log_summary(result.get("input_alignment")),
    }


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_resistant_drug(value: Optional[str]) -> str:
    if value and value.strip():
        return value.strip()
    return "Unknown"


def _prediction_label(value) -> str:
    if isinstance(value, list):
        value = value[0] if value else 0

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "1.0", "true", "resistant", "resistance"}:
            return "Resistant"
        if normalized in {"0", "0.0", "false", "sensitive", "sensitivity"}:
            return "Sensitive"

    try:
        return "Resistant" if int(float(value)) == 1 else "Sensitive"
    except (TypeError, ValueError):
        return str(value or "Unknown")


def _build_adrs_request(
    patient_id: str,
    resistant_drug: str,
    pathways: list,
    genes: list,
) -> Optional[ADRSRequest]:
    delta_e = {}
    for pathway in pathways or []:
        if not isinstance(pathway, dict):
            continue

        name = pathway.get("name")
        if not name:
            continue

        raw_score = pathway.get("weight", pathway.get("impact", pathway.get("score", 0)))
        score = abs(_safe_float(raw_score))
        if "impact" in pathway and "weight" not in pathway and score > 1:
            score = score / 100

        delta_e[str(name)] = score

    core_genes = []
    for gene in genes or []:
        if isinstance(gene, dict):
            name = gene.get("name")
        else:
            name = gene

        if name:
            core_genes.append(str(name))

    if not delta_e:
        return None

    return ADRSRequest(
        patient_id=patient_id,
        resistant_drug=resistant_drug,
        delta_e=delta_e,
        core_genes=core_genes,
        top_n=5,
        threshold=0.5,
    )


def _serialize_adrs_recommendations(adrs_response):
    return [
        recommendation.model_dump()
        for recommendation in adrs_response.recommendations
    ]


def _extract_saved_adrs_recommendations(alternatives):
    return [
        item
        for item in (alternatives or [])
        if isinstance(item, dict) and item.get("drug_name")
    ]


def _alternative_names(alternatives):
    names = []
    for item in alternatives or []:
        if isinstance(item, dict):
            name = item.get("drug_name") or item.get("name")
        else:
            name = item

        if name:
            names.append(str(name))

    return names


def _resolve_analysis_model_key(cancer_type: str) -> str:
    cancer_value = cancer_type.lower().strip()
    normalized_value = (
        cancer_value
        .replace("-", "_")
        .replace(" ", "_")
    )

    if normalized_value in MODEL_FILES:
        return normalized_value

    if "breast" in cancer_value and "multi" in cancer_value and "omics" in cancer_value:
        return "breast_multiomics"

    if "breast" in cancer_value:
        return "breast"
    if "ovarian" in cancer_value:
        return "ovarian"
    if "liver" in cancer_value:
        return "liver"
    if "immunotherapy" in cancer_value:
        return "immunotherapy"

    raise HTTPException(
        status_code=400,
        detail=f"Unsupported cancer type: {cancer_type}",
    )


def _run_adrs_recommendations(
    app,
    patient_id: str,
    resistant_drug: str,
    pathways: list,
    genes: list,
):
    adrs_request = _build_adrs_request(
        patient_id=patient_id,
        resistant_drug=resistant_drug,
        pathways=pathways,
        genes=genes,
    )

    if adrs_request is None:
        return []

    try:
        service = ADRSService.from_app_state(
            app,
            session_factory=getattr(app.state, "adrs_session_factory", None),
        )
        adrs_response = service.recommend(adrs_request)
        return _serialize_adrs_recommendations(adrs_response)
    except ValueError as exc:
        logger.warning("ADRS unavailable for %s: %s", patient_id, exc)
    except ADRSServiceError as exc:
        logger.warning("ADRS could not recommend for %s: %s", patient_id, exc)
    except Exception:
        logger.warning("ADRS recommendation failed for %s", patient_id, exc_info=True)

    return []


# -------------------- RUN ANALYSIS --------------------
@router.post("/analysis/run")
async def run_analysis(
    request: Request,
    cancerType: str = Form(...),
    resistantDrug: Optional[str] = Form(None),
    mainFile: UploadFile = File(...),
    meth_features: Optional[UploadFile] = File(None),
    cnv_features: Optional[UploadFile] = File(None),
    snv_features: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # ------------------ normalize cancer type ------------------
        model_key = _resolve_analysis_model_key(cancerType)

        # ------------------ get service ------------------
        service = model_registry.get_service(model_key)

        # ------------------ prepare files ------------------
        uploaded_files = {
            "cancer_type": cancerType,
            "geo_features": mainFile,
            "meth_features": meth_features,
            "cnv_features": cnv_features,
            "snv_features": snv_features,
        }

        # ------------------ RUN MODEL (FIXED) ------------------
        result = await service.predict_from_files(
            uploaded_files,
            include_graph=False,
        )

        logger.info(
            "Model result summary: %s",
            _model_result_log_summary(result),
        )

        # ------------------ JOB ID ------------------
        # confidence extraction
        confidence = 0.0

        try:
            if "out_multiomics_probabilities" in result:
                confidence = float(max(result["out_multiomics_probabilities"][0]))

            elif "out_probabilities" in result:
                confidence = float(max(result["out_probabilities"][0]))

        except Exception as e:
            logger.warning("Confidence extraction failed: %s", e)
            
        output = result.get("out")

        logger.info(
            "Prediction output summary: output_shape=%s output_sample=%s confidence=%.4f",
            _shape(output),
            _sample(output),
            confidence,
        )

        # prediction value
        prediction_value = 0

        if "prediction" in result:
            if isinstance(result["prediction"], list):
                prediction_value = result["prediction"][0]
            else:
                prediction_value = result["prediction"]

        elif "out" in result:
            output = result["out"]

            if isinstance(output, list) and len(output) > 0:
                prediction_value = output[0]

        job_id = "job_" + str(uuid.uuid4())[:8]
        resistant_drug = _normalize_resistant_drug(resistantDrug)

        new_prediction = PredictionHistory(
            user_id=current_user.id,
            analysis_code=job_id,
            cancer_type=cancerType,
            drug_name=resistant_drug,
            prediction_result=_prediction_label(prediction_value),
            confidence_score=confidence
        )

        db.add(new_prediction)
        db.flush()

        # ------------------ PATHWAYS ------------------
        pathways = []

        for p in result.get("structured_core_pathways", []):
            pathways.append({
                "name": p.get("name", "Unknown"),
                "impact": round(float(p.get("weight", 0)) * 100),
                "genes": []
            })


        # ------------------ GENES ------------------
        genes = []

        for g in result.get("structured_core_genes", []):
            genes.append({
                "name": g.get("name", "Unknown"),
                "score": float(g.get("score", 0)),
            })

        adrs_recommendations = _run_adrs_recommendations(
            request.app,
            patient_id=job_id,
            resistant_drug=resistant_drug,
            pathways=result.get("structured_core_pathways", []),
            genes=result.get("structured_core_genes", []),
        )
            
        # ------------------ SAVE DETAILS ------------------
        new_details = PredictionDetails(
            pathways=pathways,
            genes=genes,
            alternative_drugs=adrs_recommendations,
            interpretation="Real GC-PGE prediction completed successfully.",
        )

        # LINK RELATIONSHIP
        new_prediction.details = new_details
        db.add(new_prediction)
        db.commit()
        db.refresh(new_prediction)

        return {"job_id": job_id}

    except HTTPException:
        raise

    except ValueError as e:
        logger.warning("Analysis validation error: %s", e)
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        logger.error("ANALYSIS ERROR", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------- GET RESULT --------------------
@router.get("/analysis/{job_id}")
async def get_result(
    request: Request,
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    record = db.query(PredictionHistory).filter(
        PredictionHistory.analysis_code == job_id,
        PredictionHistory.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    details = record.details
    stored_alternatives = details.alternative_drugs if details else []
    adrs_recommendations = _extract_saved_adrs_recommendations(stored_alternatives)
    resistant_drug = _normalize_resistant_drug(record.drug_name)

    if details and not adrs_recommendations:
        adrs_recommendations = _run_adrs_recommendations(
            request.app,
            patient_id=record.analysis_code,
            resistant_drug=resistant_drug,
            pathways=details.pathways,
            genes=details.genes,
        )

        if adrs_recommendations:
            details.alternative_drugs = adrs_recommendations
            db.add(details)
            db.commit()

    return {
        "job_id": record.analysis_code,
        "cancerType": record.cancer_type,
        "resistantDrug": resistant_drug,
        "prediction": _prediction_label(record.prediction_result),
        "riskScore": int(record.confidence_score * 100) if record.confidence_score else 0,
        "pathways": details.pathways if details else [],
        "genes": details.genes if details else [],
        "interpretation": details.interpretation if details else "Pending AI interpretation...",
        "alternatives": _alternative_names(adrs_recommendations or stored_alternatives),
        "adrsRecommendations": adrs_recommendations,
    }
