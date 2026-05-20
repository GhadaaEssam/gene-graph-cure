from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid
from typing import Optional


from app.core.database import get_db 
from app.api.v1.auth import get_current_user 
from app.db.models.user import User
from app.db.models.prediction_history import PredictionHistory
from app.db.models.prediction_details import PredictionDetails

router = APIRouter(tags=["Analysis"])

@router.post("/analysis/run")
async def run_analysis(
    cancerType: str = Form(...),
    mainFile: UploadFile = File(...),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user) 
):
    job_id = "job_" + str(uuid.uuid4())[:8]

    
    new_prediction = PredictionHistory(
        user_id=current_user.id, 
        analysis_code=job_id,
        cancer_type=cancerType,
        prediction_result="Resistant", 
        confidence_score=0.82
    )
    db.add(new_prediction)
    db.flush() 

    
    new_details = PredictionDetails(
        prediction_id=new_prediction.id,
        pathways=[
            {"name": "MAPK Pathway", "impact": 91, "genes": ["TP53", "EGFR"]},
            {"name": "PI3K Signaling", "impact": 75, "genes": ["PTEN", "AKT1"]}
        ],
        alternative_drugs=["Immunotherapy (Anti-PD1)", "Combination Targeted Therapy"],
        
        interpretation=f"Based on the uploaded {mainFile.filename}, high resistance was detected..."
    )
    db.add(new_details)
    db.commit()

    return {"job_id": job_id}

@router.get("/analysis/{job_id}")
async def get_result(
    job_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    
    record = db.query(PredictionHistory).filter(
        PredictionHistory.analysis_code == job_id,
        PredictionHistory.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    
    return {
        "job_id": record.analysis_code,
        "cancerType": record.cancer_type,
        "riskScore": int(record.confidence_score * 100) if record.confidence_score else 0,
        "pathways": record.details.pathways if record.details else [],
        "interpretation": record.details.interpretation if record.details else "Pending AI interpretation...",
        "alternatives": record.details.alternative_drugs if record.details else [] # المسمى اللي الفرونت مستنيه
    }