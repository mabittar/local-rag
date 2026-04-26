from datetime import datetime
from typing import List

from pydantic import BaseModel
import uuid


class DocumentChunkResponse(BaseModel):
    id: uuid.UUID
    chunk_index: int
    content: str
    embedding: List[float]

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    file_type: str
    total_chunks: int
    status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    chunks: List[DocumentChunkResponse] = []


class DocumentListResponse(BaseModel):
    total: int
    items: List[DocumentResponse]


class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    status: str
    total_chunks: int
    message: str
    chunks: List[DocumentChunkResponse] = []
