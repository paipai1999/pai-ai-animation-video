from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "r2_storage_enabled": bool(settings.R2_ACCOUNT_ID)
    }
