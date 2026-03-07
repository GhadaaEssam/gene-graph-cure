# app/api/v1/predict.py

from fastapi import APIRouter, HTTPException
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.schemas.predict import PredictionRequest, PredictionResult
from app.services.gc_pge_service import GC_PGE_Service
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Project root (4 levels up from this file: app/api/v1/predict.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Path to weights file — injectable via environment variable
model_path = os.environ.get("MODEL_PATH", str(PROJECT_ROOT / "weights" / "liver_model.pt"))

# Validate weights file exists at startup
if not Path(model_path).exists():
    raise RuntimeError(f"Model weights not found at startup: {model_path}")

try:
    gc_pge_service = GC_PGE_Service(model_path)
    logger.info(f"Model loaded successfully from: {model_path}")
except Exception as e:
    raise RuntimeError(f"Failed to initialize GC_PGE_Service: {e}")


@router.post("/predict", response_model=PredictionResult)
def predict(data: PredictionRequest):
    try:
        raw_input = {
            "node_features": data.node_features,   # [num_nodes, num_features]
            "ppi_edges": data.ppi_edges,            # [num_edges, 2] each [src, dst]
            "homolog_edges": data.homolog_edges,    # [num_edges, 2] each [src, dst]
            "geo_features": data.geo_features       # [num_samples, num_genes]
        }
        result = gc_pge_service.predict(raw_input)
        return result

    except ValueError as e:
        # Missing or malformed input keys
        raise HTTPException(status_code=422, detail=str(e))

    except RuntimeError as e:
        # Torch/model forward pass errors
        raise HTTPException(status_code=500, detail=f"Model inference failed: {e}")

    except Exception as e:
        # Catch-all — unexpected errors
        logger.error(f"Unexpected error during prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")