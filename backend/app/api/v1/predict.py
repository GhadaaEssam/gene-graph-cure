# app/api/v1/predict.py

from fastapi import APIRouter
from app.schemas.predict import PredictionRequest, PredictionResponse
from app.services.gc_pge_service import GC_PGE_Service
import os

router = APIRouter()

# Load model once when API starts
model_path = os.environ.get("MODEL_PATH", "weights/immunotherapy_model.pt")
gc_pge_service = GC_PGE_Service(model_path)


@router.post("/predict", response_model=PredictionResponse)
def predict(data: PredictionRequest):

    raw_input = {
        "node_features": data.node_features,
        "ppi_edges": data.ppi_edges,
        "homolog_edges": data.homolog_edges,
        "geo_features": data.geo_features
    }

    return gc_pge_service.predict(raw_input)