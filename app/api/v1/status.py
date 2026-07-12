from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(tags=["status"])


@router.get("/status")
async def status() -> dict[str, str]:
    settings = get_settings()
    return {"app": settings.app_name, "environment": settings.environment, "status": "running"}
