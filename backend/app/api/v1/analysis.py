from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid
from typing import Optional
from pathlib import Path
import logging

from app.services.model_service_registry import ModelServiceRegistry
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.db.models.user import User
from app.db.models.prediction_history import PredictionHistory
from app.db.models.prediction_details import PredictionDetails

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Analysis"])

# -------------------- MODEL REGISTRY --------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
WEIGHTS_DIR = PROJECT_ROOT / "weights"
MODEL_INPUTS_DIR = PROJECT_ROOT / "model_inputs"

MODEL_FILES = {
    "liver": "liver_model.pt",
    "ovarian": "ovarian_model.pt",
    "immunotherapy": "immunotherapy_model.pt",
    "breast": "breast_model.pt",
}

model_registry = ModelServiceRegistry(
    weights_dir=WEIGHTS_DIR,
    model_inputs_dir=MODEL_INPUTS_DIR,
    model_files=MODEL_FILES,
)


# -------------------- RUN ANALYSIS --------------------
@router.post("/analysis/run")
async def run_analysis(
    cancerType: str = Form(...),
    mainFile: UploadFile = File(...),
    meth_features: Optional[UploadFile] = File(None),
    cnv_features: Optional[UploadFile] = File(None),
    snv_features: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # ------------------ normalize cancer type ------------------
        cancer_value = cancerType.lower().strip()

        if "breast" in cancer_value:
            model_key = "breast"
        elif "ovarian" in cancer_value:
            model_key = "ovarian"
        elif "liver" in cancer_value:
            model_key = "liver"
        elif "immunotherapy" in cancer_value:
            model_key = "immunotherapy"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported cancer type: {cancerType}"
            )

        # ------------------ get service ------------------
        service = model_registry.get_service(model_key)

        # ------------------ prepare files ------------------
        uploaded_files = {
            "cancer_type": cancerType,
            "geo_features": mainFile,
            "meth_features": meth_features,
            "cnv_features": cnv_features,
            "snv_features": snv_features,
        }

        # ------------------ RUN MODEL (FIXED) ------------------
        result = await service.predict_from_files(uploaded_files)

        logger.info(f"MODEL RESULT: {result}")

        # ------------------ JOB ID ------------------
        # confidence extraction
        confidence = 0.0

        try:
            if "out_probabilities" in result:
                confidence = float(max(result["out_probabilities"][0]))

            elif "out_multiomics_probabilities" in result:
                confidence = float(max(result["out_multiomics_probabilities"][0]))

        except Exception as e:
            print("CONFIDENCE ERROR:", e)
            
        print("MODEL OUTPUT:", result.get("out"))
        print("CONFIDENCE:", confidence)

        # prediction value
        prediction_value = 0

        if "prediction" in result:
            if isinstance(result["prediction"], list):
                prediction_value = result["prediction"][0]
            else:
                prediction_value = result["prediction"]

        elif "out" in result:
            output = result["out"]

            if isinstance(output, list) and len(output) > 0:
                prediction_value = output[0]

        job_id = "job_" + str(uuid.uuid4())[:8]

        new_prediction = PredictionHistory(
            user_id=current_user.id,
            analysis_code=job_id,
            cancer_type=cancerType,
            prediction_result=str(prediction_value),
            confidence_score=confidence
        )
        new_prediction = PredictionHistory(
            user_id=current_user.id,
            analysis_code=job_id,
            cancer_type=cancerType,
            prediction_result=str(prediction_value),
            confidence_score=confidence,
        )

        db.add(new_prediction)
        db.flush()

        # ------------------ PATHWAYS ------------------
        pathways = []
        for p in result.get("structured_core_pathways", []):
            pathways.append({
                "name": p.get("name", "Unknown"),
                "impact": round(float(p.get("weight", 0)) * 100),
                "genes": []
            })

        # ------------------ SAVE DETAILS ------------------
        new_details = PredictionDetails(
            prediction_id=new_prediction.id,
            pathways=pathways,
            alternative_drugs=["Recommended targeted therapy"],
            interpretation="Real GC-PGE prediction completed successfully.",
        )

        db.add(new_details)
        db.commit()

        return {"job_id": job_id}

    except Exception as e:
        logger.error("ANALYSIS ERROR", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------- GET RESULT --------------------
@router.get("/analysis/{job_id}")
async def get_result(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
        "alternatives": record.details.alternative_drugs if record.details else []
    }