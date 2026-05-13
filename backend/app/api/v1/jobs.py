# app/api/v1/jobs.py
from fastapi import APIRouter
from app.schemas.predict import JobStatus

router = APIRouter()

@router.get("/jobs/{job_id}")
def job_status(job_id: str):
    # In the real system, we will query a database or background task queue
    # For now, we return a fixed status (can be replaced with Celery/RQ/Prefect)
    return {
        "job_id": job_id,
        "status": JobStatus.RUNNING
    }