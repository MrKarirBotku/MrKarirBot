from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl

from app.api.dependencies.auth import require_user
from app.core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthConfig(BaseModel):
    supabase_url: HttpUrl
    publishable_key: str


class CurrentUser(BaseModel):
    id: UUID
    email: str | None = None
    role: str


@router.get("/config", response_model=AuthConfig)
async def auth_config() -> AuthConfig:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_publishable_key:
        raise HTTPException(status_code=503, detail="Supabase Auth belum dikonfigurasi")
    return AuthConfig(
        supabase_url=settings.supabase_url,
        publishable_key=settings.supabase_publishable_key,
    )


@router.get("/me", response_model=CurrentUser)
async def current_user(
    user: Annotated[dict[str, str | UUID | None], Depends(require_user)],
) -> CurrentUser:
    return CurrentUser.model_validate(user)
