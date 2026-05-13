# app/schemas/common.py
from pydantic import BaseModel
from typing import Optional, Dict

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[Dict] = None