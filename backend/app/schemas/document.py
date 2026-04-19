from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DocumentChunkResponse(BaseModel):
    id: str
    chunk_index: int
    content: str
    page_number: Optional[int] = None

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
