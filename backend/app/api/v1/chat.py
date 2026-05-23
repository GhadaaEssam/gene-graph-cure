from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.db.models.user import User
from app.db.models.prediction_history import PredictionHistory

from app.services.ai_agent.llm_client import generate_text

router = APIRouter(prefix="/chat", tags=["AI Chat"])


class ChatMessage(BaseModel):
    message: str
    job_id: Optional[str] = None


def _requested_cancer_type(message: str) -> Optional[str]:
    message = message.lower()

    for cancer_type in ("immunotherapy", "ovarian", "liver", "breast"):
        if cancer_type in message:
            return cancer_type

    return None


def _asks_for_latest_analysis(message: str) -> bool:
    message = message.lower()
    return (
        ("last" in message or "latest" in message or "recent" in message)
        and ("analysis" in message or "result" in message)
    )


def _latest_analysis_for_message(
    db: Session,
    current_user: User,
    message: str,
) -> Optional[PredictionHistory]:
    requested_cancer_type = _requested_cancer_type(message)

    query = db.query(PredictionHistory).filter(
        PredictionHistory.user_id == current_user.id
    )

    if requested_cancer_type:
        query = query.filter(
            PredictionHistory.cancer_type.ilike(f"%{requested_cancer_type}%")
        )

    return query.order_by(PredictionHistory.analysis_date.desc()).first()


@router.post("/send")
async def send_chat_message(
    payload: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    current_time = datetime.now().strftime("%I:%M %p")

    # ---------------- LOAD ANALYSIS ----------------
    analysis = None

    if payload.job_id:

        analysis = db.query(PredictionHistory).filter(
            PredictionHistory.analysis_code == payload.job_id,
            PredictionHistory.user_id == current_user.id
        ).first()

    requested_cancer_type = _requested_cancer_type(payload.message)

    if (
        analysis
        and requested_cancer_type
        and _asks_for_latest_analysis(payload.message)
        and requested_cancer_type not in (analysis.cancer_type or "").lower()
    ):
        analysis = None

    if not analysis:
        analysis = _latest_analysis_for_message(
            db=db,
            current_user=current_user,
            message=payload.message,
        )

    # ---------------- NO ANALYSIS ----------------
    if not analysis:

        return {
            "reply": "I couldn't find an analysis result to reference. Please run an analysis first or open one from Results.",
            "timestamp": current_time
        }

    details = analysis.details

    # ---------------- BUILD CONTEXT ----------------
    pathways_text = ""
    pathways = details.pathways if details and details.pathways else []

    for p in pathways:
        pathways_text += (
            f"- {p.get('name', 'Unknown')} "
            f"(Impact: {p.get('impact', 0)}%)\n"
        )

    genes_text = ""
    genes = details.genes if details and details.genes else []

    for g in genes:
        genes_text += (
            f"- {g.get('name', 'Unknown')} "
            f"(Score: {g.get('score', 0)})\n"
        )

    # ---------------- PROMPT ----------------
    prompt = f"""
You are a biomedical AI assistant.

Patient Analysis:
Analysis ID: {analysis.analysis_code}

Cancer Type: {analysis.cancer_type}

Prediction: {analysis.prediction_result}

Confidence: {analysis.confidence_score}

Top Pathways:
{pathways_text}

Top Genes:
{genes_text}

User Question:
{payload.message}

Answer clearly and medically.
"""

    # ---------------- OLLAMA ----------------
    reply = generate_text(prompt)

    return {
        "reply": reply,
        "timestamp": current_time,
        "job_id": analysis.analysis_code
    }
