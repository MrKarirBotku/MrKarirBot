from typing import Annotated
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)


async def require_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> dict[str, str | UUID | None]:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token wajib disertakan"
        )
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_publishable_key:
        raise HTTPException(status_code=503, detail="Supabase Auth belum dikonfigurasi")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{settings.supabase_url.rstrip('/')}/auth/v1/user",
                headers={
                    "apikey": settings.supabase_publishable_key,
                    "Authorization": f"Bearer {credentials.credentials}",
                },
            )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Supabase Auth sementara tidak tersedia") from exc

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Token tidak valid atau sudah kedaluwarsa")

    payload = response.json()
    app_metadata = payload.get("app_metadata") or {}
    return {
        "id": UUID(payload["id"]),
        "email": payload.get("email"),
        "role": str(app_metadata.get("role", "user")),
    }


async def require_admin(
    current_user: Annotated[dict[str, str | UUID | None], Depends(require_user)],
) -> dict[str, str | UUID | None]:
    if current_user["role"] not in {"admin", "superadmin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses admin diperlukan")
    return current_user
