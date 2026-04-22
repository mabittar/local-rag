from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import (
    ChatMessageListResponse,
    ChatMessageResponse,
    ChatSessionListResponse,
    ChatSessionResponse,
)


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        user_id: int,
        title: Optional[str] = None,
    ) -> ChatSessionResponse:
        if not title:
            title = "Nova Conversa"

        session = ChatSession(
            user_id=user_id,
            title=title,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return ChatSessionResponse.model_validate(session)

    async def list_sessions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> ChatSessionListResponse:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        sessions = result.scalars().all()

        count_result = await self.db.execute(
            select(ChatSession).where(ChatSession.user_id == user_id)
        )
        total = len(count_result.scalars().all())

        return ChatSessionListResponse(
            total=total,
            items=[ChatSessionResponse.model_validate(s) for s in sessions],
        )

    async def get_session(
        self,
        session_id: int,
        user_id: int,
    ) -> Optional[ChatSession]:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def delete_session(self, session_id: int, user_id: int) -> bool:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            return False

        await self.db.delete(session)
        await self.db.commit()
        return True

    async def get_session_messages(
        self,
        session_id: int,
        user_id: int,
    ) -> Optional[ChatMessageListResponse]:
        session = await self.get_session(session_id, user_id)
        if not session:
            return None

        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        messages = result.scalars().all()

        return ChatMessageListResponse(
            session_id=session_id,
            messages=[ChatMessageResponse.model_validate(m) for m in messages],
        )

    async def save_message(
        self,
        session_id: int,
        role: str,
        content: str,
        sources: Optional[List[dict]] = None,
    ) -> ChatMessageResponse:
        sources_data = sources if sources else None

        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources_data,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        return ChatMessageResponse.model_validate(message)

    async def update_session_timestamp(self, session_id: int) -> None:
        from datetime import datetime
        from sqlalchemy import update

        await self.db.execute(
            update(ChatSession)
            .where(ChatSession.id == session_id)
            .values(updated_at=datetime.utcnow())
        )
        await self.db.commit()
