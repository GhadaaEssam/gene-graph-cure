from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from app.schemas.predict import ModelKey, PredictionResult
from app.services.model_service_registry import ModelServiceRegistry
from pathlib import Path
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Project root setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
WEIGHTS_DIR = PROJECT_ROOT / "weights"
MODEL_INPUTS_DIR = PROJECT_ROOT / "model_inputs"

# Lazy-load services as each model is requested.
model_registry = ModelServiceRegistry(
    weights_dir=WEIGHTS_DIR,
    model_inputs_dir=MODEL_INPUTS_DIR,
    model_files={
        "liver": "liver_model.pt",
        "ovarian": "ovarian_model.pt",
        "immunotherapy": "immunotherapy_model.pt",
    },
)

@router.post("/predict", response_model=PredictionResult)
async def predict(
    geo_features: UploadFile = File(...),
    model: ModelKey = Form(...),
):
    """
    Run GC-PGE model inference using patient GEO features and static model inputs.
    """
    try:
        service = model_registry.get_service(model.value)
        static_inputs_dir = model_registry.get_static_inputs_dir(model.value)
        logger.info("Running prediction with model: %s", model)

        result = await service.predict_from_geo_file(
            geo_features=geo_features,
            static_inputs_dir=static_inputs_dir,
        )

        return result

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    except FileNotFoundError as e:
        logger.error(f"Model configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    except RuntimeError as e:
        logger.error(f"Inference failure: {e}")
        raise HTTPException(status_code=500, detail=f"Model inference failed: {e}")

    except Exception as e:
        logger.error("Unexpected error during prediction", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")