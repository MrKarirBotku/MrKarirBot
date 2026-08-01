import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from redis.asyncio import from_url
from sqlalchemy import text

from app.core.config import get_settings
from app.database.session import engine

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "MrKarirBot"}


@router.get("/ready")
async def readiness() -> JSONResponse:
    settings = get_settings()
    checks = {"database": False, "redis": False}
    try:
        async with engine.connect() as connection:
            await connection.execute(text("select 1"))
        checks["database"] = True
    except Exception as exc:  # noqa: BLE001
        logger.warning("readiness_check_failed dependency=database error=%s", type(exc).__name__)

    client = from_url(settings.redis_url)
    try:
        checks["redis"] = bool(await client.ping())
    except Exception as exc:  # noqa: BLE001
        logger.warning("readiness_check_failed dependency=redis error=%s", type(exc).__name__)
    finally:
        await client.aclose()

    ready = all(checks.values())
    return JSONResponse(
        status_code=200 if ready else 503,
        content={"status": "ready" if ready else "not_ready", "checks": checks},
    )
