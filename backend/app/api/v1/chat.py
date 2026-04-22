import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.infrastructure.openrouter import OpenRouterClient
from app.infrastructure.pgvector_store import PGVectorStore
from app.models.user import User
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionListResponse,
    ChatSessionResponse,
)
from app.services.chat_service import ChatService
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter()


def format_sse(data: str, event: str = "message") -> str:
    return f"event: {event}\ndata: {data}\n\n"


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatSessionResponse:
    service = ChatService(db)
    return await service.create_session(
        user_id=current_user.id,
        title=data.title,
    )


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_sessions(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatSessionListResponse:
    service = ChatService(db)
    return await service.list_sessions(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = ChatService(db)
    deleted = await service.delete_session(session_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    result = await service.get_session_messages(session_id, current_user.id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )

    return result


@router.get("/stream")
async def chat_stream(
    session_id: int,
    message: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chat_service = ChatService(db)
    session = await chat_service.get_session(session_id, current_user.id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )

    await chat_service.save_message(
        session_id=session_id,
        role="user",
        content=message,
    )

    vector_store = PGVectorStore(db)
    openrouter = OpenRouterClient()
    rag_service = RAGService(vector_store, openrouter)

    chunks, context = await rag_service.retrieve_context(message, top_k=5)

    sources = [
        {
            "chunk_id": chunk["id"],
            "document_id": chunk["document_id"],
            "similarity": chunk["similarity"],
            "content_preview": chunk["content"][:200],
        }
        for chunk in chunks
    ]

    async def generate_stream() -> AsyncGenerator[str, None]:
        full_response = ""
        try:
            async for token in rag_service.stream_chat_response(
                query=message,
                context=context,
            ):
                if token:
                    full_response += token
                    yield format_sse(
                        json.dumps({"type": "token", "data": token}),
                        event="message"
                    )

            if sources:
                yield format_sse(
                    json.dumps({"type": "sources", "sources": sources}),
                    event="message"
                )

            await chat_service.save_message(
                session_id=session_id,
                role="assistant",
                content=full_response,
                sources=sources,
            )

            await chat_service.update_session_timestamp(session_id)

            yield format_sse(
                json.dumps({"type": "done"}),
                event="message"
            )
        except Exception as e:
            logger.error(f"Error in chat stream: {e}")
            yield format_sse(
                json.dumps({"type": "error", "message": str(e)}),
                event="message"
            )

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
