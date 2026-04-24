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

@router.get("/analyses/{job_id}")
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

# قاعدة بيانات وهمية لتخزين النتائج مؤقتاً
# FAKE_DB = {}

# @router.post("/analysis/run")
# async def run_analysis(
#     cancerType: str = Form(...),
#     mainFile: UploadFile = File(...),
#     mutationFile: Optional[UploadFile] = File(None),
#     cnvFile: Optional[UploadFile] = File(None),
#     methFile: Optional[UploadFile] = File(None)
# ):
#     # 1. تكوين ID فريد للعملية
#     job_id = "job_" + str(uuid.uuid4())[:8]

#     # 2. هنا المفروض كود الـ AI بتاعك يشتغل على الملفات
#     # حالياً هنخزن داتا تجريبية مرتبطة بالـ job_id ده
#     FAKE_DB[job_id] = {
#         "job_id": job_id,
#         "cancerType": cancerType,
#         "riskScore": 82,
#         "pathways": [
#             {"name": "MAPK Pathway", "impact": 91, "genes": ["TP53", "EGFR"]},
#             {"name": "PI3K Signaling", "impact": 75, "genes": ["PTEN", "AKT1"]}
#         ],
#         "interpretation": f"Based on the uploaded {mainFile.filename}, high resistance was detected for standard treatments in {cancerType}.",
#         "alternatives": ["Immunotherapy (Anti-PD1)", "Combination Targeted Therapy"]
#     }

#     return {"job_id": job_id}

# @router.get("/analyses/{job_id}")
# async def get_result(job_id: str):
    
#     if job_id in FAKE_DB:
#         return FAKE_DB[job_id]
    
#     # 2. لو مش موجود (عشان السيرفر رستر مثلاً)، بنرجع "Fallback Data" 
#     # عشان الفرونت إند يعرض شكل الصفحة وما يظهرش Error بيضايق اليوزر
#     return {
#         "job_id": job_id,
#         "cancerType": "Lung Cancer (Demo Data)",
#         "riskScore": 75,
#         "pathways": [
#             {
#                 "name": "Apoptosis Pathway", 
#                 "impact": 85, 
#                 "genes": ["BAX", "CASP3", "BCL2"]
#             },
#             {
#                 "name": "Cell Cycle", 
#                 "impact": 60, 
#                 "genes": ["CDK4", "CCND1"]
#             }
#         ],
#         "interpretation": "Note: This is demo data because the specific job record was cleared from server memory. In a production environment, this would be fetched from a permanent database.",
#         "alternatives": ["Standard Chemotherapy", "Experimental Targeted Therapy"]
#     }