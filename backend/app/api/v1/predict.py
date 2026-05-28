from pathlib import Path
from typing import Optional
import logging
import pandas as pd
import io

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from pydantic import ValidationError

from app.schemas.predict import ModelKey, PredictionRequest, PredictionResult
from app.services.model_service_registry import ModelServiceRegistry

# RAG service
from app.services.rag_service import RAGService


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

# Initialize RAG service
try:
    rag_service = RAGService()
    logger.info("RAG Service initialized successfully.")
except Exception as e:
    rag_service = None
    logger.warning(f"RAG Service failed to start: {e}")


@router.post("/predict", response_model=PredictionResult)
async def predict(
    geo_features: UploadFile = File(...),
    model: ModelKey = Form(...),
    include_graph: bool = Query(
        False,
        description="Return the full learned graph matrix. Disabled by default to avoid huge responses.",
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

        logger.info(
            "Running prediction with model: %s",
            request.model.value
        )

        # Run prediction
        result = await service.predict_from_files(
            request.uploaded_files,
            include_graph=request.include_graph,
        )

        # ---------------- RAG INTEGRATION ----------------
        if rag_service is not None:
            try:
                await geo_features.seek(0)

                geo_content = await geo_features.read()

                geo_df = pd.read_csv(
                    io.BytesIO(geo_content),
                    header=0
                )

                evidence = rag_service.generate_evidence(
                    result,
                    geo_df
                )

                result["rag_evidence"] = evidence

            except Exception as rag_error:
                logger.warning(
                    "RAG generation failed: %s",
                    rag_error
                )
        # ------------------------------------------------

        return result

    except (ValueError, ValidationError) as e:
        logger.warning("Validation error: %s", e)
        raise HTTPException(status_code=422, detail=str(e))

    except FileNotFoundError as e:
        logger.error("Model configuration error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    except RuntimeError as e:
        logger.error("Inference failure: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Model inference failed: {e}"
        )

    except Exception as e:
        logger.error(
            "Unexpected error during prediction",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {e}"
        )
