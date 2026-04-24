from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/chat", tags=["AI Chat"])

# موديل لاستقبال الرسالة
class ChatMessage(BaseModel):
    message: str
    job_id: Optional[str] = None

@router.post("/send")
async def send_chat_message(payload: ChatMessage):
    user_msg = payload.message.lower()
    
    # تحديد الوقت الحالي بنفس التنسيق اللي الفرونت مستنيه
    current_time = datetime.now().strftime("%I:%M %p")

    # الرد الافتراضي (Default)
    reply = "That's a very insightful question about the genomic profile. I'm currently cross-referencing this with our database of known genetic pathways. Would you like to focus on a specific gene?"

    # رد مخصص لو اليوزر سأل عن المقاومة (Resistance)
    if "resistant" in user_msg or "resistance" in user_msg:
        reply = (
            "Based on the genomic analysis, the patient shows resistance due to several key factors:\n\n"
            "**1. MAPK/ERK Pathway Activation**: High activation (87%) detected, driven by KRAS/BRAF mutations.\n"
            "**2. PI3K/AKT Pathway**: Secondary resistance via PIK3CA alterations (72% impact).\n"
            "**3. DNA Repair**: Enhanced damage response (65% impact) allowing cell survival.\n\n"
            "These mechanisms collectively create multiple escape routes for cancer cells."
        )
    
    # رد مخصص لو سأل عن العلاجات
    elif "treatment" in user_msg or "drug" in user_msg:
        reply = (
            "Looking at the predicted resistance profile, **Immunotherapy** or **Combination Targeted Therapy** "
            "show the highest potential for overcoming these bypass mechanisms. We recommend checking the alternative treatments section."
        )

    return {
        "reply": reply,
        "timestamp": current_time
    }