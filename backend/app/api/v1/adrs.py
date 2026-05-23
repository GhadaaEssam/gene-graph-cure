# app/api/v1/adrs.py
import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.schemas.adrs import ADRSRequest, ADRSResponse
from app.services.adrs_service import ADRSService, ADRSServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/adrs", tags=["ADRS"])


@router.post("/recommend", response_model=ADRSResponse)
async def recommend(request: Request, body: ADRSRequest):
    try:
        service = ADRSService.from_app_state(
            request.app,
            session_factory=getattr(request.app.state, "adrs_session_factory", None)
        )
        return service.recommend(body)
    except ValueError as e:
        raise HTTPException(status_code=503, detail={"error": str(e), "code": "DB_UNAVAILABLE"})
    except ADRSServiceError as e:
        raise HTTPException(status_code=422, detail={"error": e.message, "code": e.code})
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": "Internal error.", "code": "INTERNAL_ERROR"})


@router.get("/health")
async def health(request: Request):
    try:
        service = ADRSService.from_app_state(request.app)
        return service.health()
    except ValueError:
        return JSONResponse(status_code=503, content={"status": "unavailable", "reason": "Graph not loaded"})