from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.security import ALGORITHM

bearer_scheme = HTTPBearer(auto_error=False)


def require_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> dict[str, str]:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token wajib disertakan"
        )
    try:
        payload = jwt.decode(
            credentials.credentials, get_settings().secret_key, algorithms=[ALGORITHM]
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid"
        ) from exc
    return {"subject": str(payload.get("sub")), "role": str(payload.get("role", "user"))}


def require_admin(
    current_user: Annotated[dict[str, str], Depends(require_user)],
) -> dict[str, str]:
    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses admin diperlukan")
    return current_user
