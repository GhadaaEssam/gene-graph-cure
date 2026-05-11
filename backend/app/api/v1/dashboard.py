# from fastapi import APIRouter
# from datetime import datetime

# router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# @router.get("/summary")
# async def get_summary():
#     # في المستقبل، الداتا دي هتيجي من DB بـ count() و sum()
#     return {
#         "totalAnalyses": 170,
#         "resistant": 57,
#         "sensitive": 70,
#         "topPathway": "MAPK/ERK",
#         "topPathwayCount": 28,
#     }

# @router.get("/recent")
# async def get_recent():
#     # محاكاة للبيانات الأخيرة، دي هتكون SELECT * FROM analyses ORDER BY date DESC
#     return [
#         {
#             "id": "P-101",
#             "drug": "Osimertinib",
#             "prediction": "Resistant",
#             "confidence": 89,
#             "date": datetime.now().strftime("%Y-%m-%d"),
#         },
#         {
#             "id": "P-102",
#             "drug": "Gefitinib",
#             "prediction": "Sensitive",
#             "confidence": 92,
#             "date": "2024-12-17",
#         },
#         {
#             "id": "P-103",
#             "drug": "Erlotinib",
#             "prediction": "Resistant",
#             "confidence": 76,
#             "date": "2024-12-16",
#         }
#     ]

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.db.models.prediction_history import PredictionHistory
from app.db.models.user import User
from app.api.v1.auth import get_current_user 
from sqlalchemy import func

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/summary")
async def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_query = db.query(PredictionHistory).filter(PredictionHistory.user_id == current_user.id)
    
    total = user_query.count()
    resistant = user_query.filter(PredictionHistory.prediction_result == "Resistant").count()
    sensitive = user_query.filter(PredictionHistory.prediction_result == "Sensitive").count()
    
    return {
        "doctorName": current_user.full_name,
        "totalAnalyses": total,
        "resistant": resistant,
        "sensitive": sensitive,
        "topPathway": "MAPK/ERK",
        "topPathwayCount": 28
    }

@router.get("/recent")
async def get_recent(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recent_records = db.query(PredictionHistory)\
        .filter(PredictionHistory.user_id == current_user.id)\
        .order_by(PredictionHistory.analysis_date.desc())\
        .limit(5).all()
    
    return [
        {
            "id": rec.analysis_code, # ده اللي بيظهر في خانة Patient ID
            "analysis_code": rec.analysis_code, # 👈 ضيفي السطر ده عشان الفرونت يستخدمه في اللينك
            "drug": rec.drug_name if rec.drug_name else "N/A",
            "prediction": rec.prediction_result,
            "confidence": int(rec.confidence_score * 100) if rec.confidence_score else 0,
            "date": rec.analysis_date.strftime("%Y-%m-%d") if rec.analysis_date else "N/A"
        } for rec in recent_records
    ]