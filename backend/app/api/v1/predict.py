from fastapi import APIRouter, HTTPException, File, Query, UploadFile
from app.schemas.predict import PredictionResult
from app.services.gc_pge_service import GC_PGE_Service
from pathlib import Path
from typing import Optional
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Project root setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Model path setup
model_path = os.environ.get(
    "MODEL_PATH",
    str(PROJECT_ROOT / "weights" / "liver_model.pt")
)

multiomics_model_paths_env = os.environ.get("MULTIOMICS_MODEL_PATHS")
if multiomics_model_paths_env:
    multiomics_model_paths = [
        path.strip()
        for path in multiomics_model_paths_env.split(",")
        if path.strip()
    ]
else:
    multiomics_model_dir = Path(os.environ.get(
        "MULTIOMICS_MODEL_DIR",
        str(PROJECT_ROOT / "weights")
    ))
    multiomics_model_paths = [
        str(path)
        for path in (
            multiomics_model_dir / f"model_multiomics_Fold_{fold}.pt"
            for fold in range(1, 6)
        )
        if path.exists()
    ]

# Validate model file exists at startup
if not Path(model_path).exists():
    raise RuntimeError(f"Model weights not found at startup: {model_path}")

# Initialize Service once
try:
    gc_pge_service = GC_PGE_Service(model_path, multiomics_model_paths=multiomics_model_paths)
    logger.info(f"Model loaded successfully from: {model_path}")
    if multiomics_model_paths:
        logger.info(f"Multi-omics models loaded: {multiomics_model_paths}")
except Exception as e:
    raise RuntimeError(f"Failed to initialize GC_PGE_Service: {e}")

@router.post("/predict", response_model=PredictionResult)
async def predict(
    include_graph: bool = Query(
        True,
        description="Return the full learned graph matrix. Leave false in Swagger for faster display."
    ),
    geo_features: UploadFile = File(...),
    anchor_genes: UploadFile = File(...),
    node_features: UploadFile = File(...),
    ppi_edges: UploadFile = File(...),
    homolog_edges: UploadFile = File(...),
    meth_features: Optional[UploadFile] = File(None),
    cnv_features: Optional[UploadFile] = File(None),
    snv_features: Optional[UploadFile] = File(None)
):
    """
    Run GC-PGE model inference using multipart file uploads.
    Upload only the required files for the base RNA model. Upload all three
    optional omics files to switch to the multi-omics late-fusion model.
    """
    try:
        # We pass the file objects directly to the service
        # The service will call .read() and use pd.read_csv()
        raw_files = {
            "geo_features": geo_features,
            "anchor_genes": anchor_genes,
            "node_features": node_features,
            "ppi_edges": ppi_edges,
            "homolog_edges": homolog_edges,
            "meth_features": meth_features,
            "cnv_features": cnv_features,
            "snv_features": snv_features
        }

        # The service will handle reading the files, preprocessing, and prediction
        result = await gc_pge_service.predict_from_files(
            raw_files,
            include_graph=include_graph
        )

        return result

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    except RuntimeError as e:
        logger.error(f"Inference failure: {e}")
        raise HTTPException(status_code=500, detail=f"Model inference failed: {e}")

    except Exception as e:
        logger.error("Unexpected error during prediction", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
