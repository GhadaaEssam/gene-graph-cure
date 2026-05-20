import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile

from app.schemas.predict import ModelKey, PredictionResult
from app.services.gc_pge_service import GC_PGE_Service

logger = logging.getLogger(__name__)

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
WEIGHTS_DIR = PROJECT_ROOT / "weights"

MODEL_PATHS = {
    "liver": str(WEIGHTS_DIR / "liver_model.pt"),
    "ovarian": str(WEIGHTS_DIR / "ovarian_model.pt"),
    "immunotherapy": str(WEIGHTS_DIR / "immunotherapy_model.pt"),
    "breast": str(WEIGHTS_DIR / "breast_model.pt"),
}
MULTIOMICS_MODEL_PATH = str(WEIGHTS_DIR / "final_multiomics_model.pt")

try:
    gc_pge_service = GC_PGE_Service(
        model_paths=MODEL_PATHS,
        multiomics_model_path=MULTIOMICS_MODEL_PATH,
    )
    logger.info("Prediction service initialized with models: %s", ", ".join(MODEL_PATHS))
except Exception as e:
    raise RuntimeError(f"Failed to initialize GC_PGE_Service: {e}") from e


@router.post("/predict", response_model=PredictionResult)
async def predict(
    include_graph: bool = Query(
        False,
        description="Return the full learned graph matrix. Leave false in Swagger for faster display.",
    ),
    geo_features: UploadFile = File(...),
    cancer_type: Optional[ModelKey] = Form(None),
    model: Optional[ModelKey] = Form(None),
    meth_features: Optional[UploadFile] = File(None),
    cnv_features: Optional[UploadFile] = File(None),
    snv_features: Optional[UploadFile] = File(None),
):
    """
    Run GC-PGE inference from uploaded GEO features.

    Base RNA models are selected by cancer_type. For breast cancer, uploading all
    three optional omics files routes the request to the multi-omics model.
    """
    try:
        selected_model = cancer_type or model
        if selected_model is None:
            raise ValueError("Either cancer_type or model must be provided.")

        raw_files = {
            "cancer_type": selected_model.value,
            "geo_features": geo_features,
            "meth_features": meth_features,
            "cnv_features": cnv_features,
            "snv_features": snv_features,
        }

        return await gc_pge_service.predict_from_files(
            raw_files,
            include_graph=include_graph,
        )

    except ValueError as e:
        logger.warning("Validation error: %s", e)
        raise HTTPException(status_code=422, detail=str(e)) from e

    except FileNotFoundError as e:
        logger.error("Model configuration error: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e

    except RuntimeError as e:
        logger.error("Inference failure: %s", e)
        raise HTTPException(status_code=500, detail=f"Model inference failed: {e}") from e

    except Exception as e:
        logger.error("Unexpected error during prediction", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}") from e
