from fastapi import APIRouter
from app.api.v1 import ai, health, status, telegram
from app.api.v1.endpoints import auth, jobs

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(status.router)
api_router.include_router(ai.router)
api_router.include_router(auth.router)
api_router.include_router(jobs.router)
api_router.include_router(telegram.router)
