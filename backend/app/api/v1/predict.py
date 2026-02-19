# app/api/v1/predict.py
from fastapi import APIRouter
from app.schemas.predict import PredictionRequest, JobStatus

router = APIRouter()

@router.post("/predict")
def predict(data: PredictionRequest):
    return {
        "job_id": "123",
        "status": JobStatus.PENDING
    }