from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    title: Optional[str] = "Nova Conversa"


class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatSessionListResponse(BaseModel):
    total: int
    items: List[ChatSessionResponse]


class ChatMessageSource(BaseModel):
    chunk_id: str
    document_id: int
    similarity: float
    content_preview: str


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: Optional[List[ChatMessageSource]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageListResponse(BaseModel):
    session_id: int
    messages: List[ChatMessageResponse]


class ChatStreamRequest(BaseModel):
    session_id: int
    message: str


class ChatStreamResponse(BaseModel):
    type: str  # "token", "sources", "done"
    data: Optional[str] = None
    sources: Optional[List[ChatMessageSource]] = None
