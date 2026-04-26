from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(
        default="Nova Conversa",
        sa_column=Column(String(255), nullable=False, server_default="Nova Conversa")
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True))
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    )

    user: Optional["User"] = Relationship(back_populates="sessions")
    messages: List["ChatMessage"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "order_by": "ChatMessage.created_at"}
    )


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("ix_chat_messages_sources", "sources", postgresql_using="gin"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chat_sessions.id", nullable=False, index=True)
    role: str = Field(sa_column=Column(String(20), nullable=False))
    content: str = Field(sa_column=Column(Text, nullable=False))
    sources: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB)
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default="now()")
    )

    session: Optional["ChatSession"] = Relationship(back_populates="messages")
