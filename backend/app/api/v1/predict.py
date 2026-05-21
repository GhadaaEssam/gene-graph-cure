from pathlib import Path
from typing import Optional
import logging

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from pydantic import ValidationError

from app.schemas.predict import ModelKey, PredictionRequest, PredictionResult
from app.services.model_service_registry import ModelServiceRegistry


logger = logging.getLogger(__name__)
router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
WEIGHTS_DIR = PROJECT_ROOT / "weights"
MODEL_INPUTS_DIR = PROJECT_ROOT / "model_inputs"
MODEL_FILES = {
    "liver": "liver_model.pt",
    "ovarian": "ovarian_model.pt",
    "immunotherapy": "immunotherapy_model.pt",
    "colorectal": "colorectal_model.pt",
    "breast": "breast_model.pt",
    "breast_multiomics": "final_multiomics_model.pt",
}

model_registry = ModelServiceRegistry(
    weights_dir=WEIGHTS_DIR,
    model_inputs_dir=MODEL_INPUTS_DIR,
    model_files=MODEL_FILES,
)


@router.post("/predict", response_model=PredictionResult)
async def predict(
    geo_features: UploadFile = File(...),
    model: ModelKey = Form(...),
    include_graph: bool = Query(
        True,
        description="Return the full learned graph matrix. Set false for faster responses.",
    ),
    meth_features: Optional[UploadFile] = File(None),
    cnv_features: Optional[UploadFile] = File(None),
    snv_features: Optional[UploadFile] = File(None),
):
    """
    Run GC-PGE inference.

    Use `model=breast_multiomics` with all four omics files:
    `geo_features` for RNA plus `meth_features`, `cnv_features`, and `snv_features`.
    Other models use only `geo_features`.
    """
    try:
        request = PredictionRequest(
            model=model,
            geo_features=geo_features,
            include_graph=include_graph,
            meth_features=meth_features,
            cnv_features=cnv_features,
            snv_features=snv_features,
        )

        service = model_registry.get_service(request.model.value)
        logger.info("Running prediction with model: %s", request.model.value)
        return await service.predict_from_files(
            request.uploaded_files,
            include_graph=request.include_graph,
        )

    except (ValueError, ValidationError) as e:
        logger.warning("Validation error: %s", e)
        raise HTTPException(status_code=422, detail=str(e))

    except FileNotFoundError as e:
        logger.error("Model configuration error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    except RuntimeError as e:
        logger.error("Inference failure: %s", e)
        raise HTTPException(status_code=500, detail=f"Model inference failed: {e}")

    except Exception as e:
        logger.error("Unexpected error during prediction", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")