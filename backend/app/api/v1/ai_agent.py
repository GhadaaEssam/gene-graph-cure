from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_agent.ai_service import (
    run_ai_analysis,
    ask_ai,
)

router = APIRouter()


class AIAnalysisRequest(BaseModel):
    analysis_result: dict
    cancer_type: str | None = None
    drug: str | None = None


class AIChatRequest(BaseModel):
    question: str
    analysis_result: dict


@router.post("/generate-report")
def generate_report(request: AIAnalysisRequest):

    return run_ai_analysis(
        analysis_result=request.analysis_result,
        cancer_type=request.cancer_type,
        drug=request.drug,
    )


@router.post("/chat")
def chat(request: AIChatRequest):

    answer = ask_ai(
        request.question,
        request.analysis_result,
    )

    return {
        "answer": answer
    }