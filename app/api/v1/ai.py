from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.dependencies.auth import require_user
from app.services.ai.service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=8000)


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    _user: Annotated[dict[str, str | UUID | None], Depends(require_user)],
) -> ChatResponse:
    return ChatResponse(answer=await AIService().career_chat(payload.message))
