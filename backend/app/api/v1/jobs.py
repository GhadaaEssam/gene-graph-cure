# app/api/v1/jobs.py
from fastapi import APIRouter
from app.schemas.predict import JobStatus

router = APIRouter()

@router.get("/jobs/{job_id}")
def job_status(job_id: str):
    return {
        "job_id": job_id,
        "status": JobStatus.RUNNING
    }