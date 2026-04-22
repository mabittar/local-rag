from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
import uuid_utils

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(sa_column=Column(String(255), nullable=False))
    file_path: str = Field(sa_column=Column(String(500), nullable=False))
    file_size: int = Field(sa_column=Column(BigInteger, nullable=False))
    file_type: str = Field(sa_column=Column(String(50), nullable=False))
    total_chunks: int = Field(default=0, sa_column=Column(Integer, server_default="0"))
    status: str = Field(
        default="processing",
        sa_column=Column(String(20), nullable=False, server_default="processing"),
    )
    uploaded_by: int = Field(foreign_key="users.id", nullable=False)
    uploaded_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow),
    )

    user: Optional["User"] = Relationship(back_populates="documents")
    chunks: List["DocumentChunk"] = Relationship(
        back_populates="document",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class DocumentChunk(SQLModel, table=True):
    __tablename__ = "document_chunks"

    id: UUID = Field(default_factory=uuid_utils.uuid7, primary_key=True)
    document_id: int = Field(foreign_key="documents.id", nullable=False, index=True)
    chunk_index: int = Field(sa_column=Column(Integer, nullable=False))
    content: str = Field(sa_column=Column(Text, nullable=False))
    embedding: Optional[List[float]] = Field(
        default=None, sa_column=Column(Vector(384))
    )
    page_number: Optional[int] = Field(default=None, sa_column=Column(Integer))
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True))
    )

    document: Optional["Document"] = Relationship(back_populates="chunks")
