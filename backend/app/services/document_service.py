import os
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.infrastructure.document_processor import DocumentProcessor
from app.infrastructure.openrouter import OpenRouterClient
from app.models.document import Document, DocumentChunk
from app.schemas.document import (
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
)


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.processor = DocumentProcessor()
        self.openrouter = OpenRouterClient()

    async def upload_document(
        self,
        filename: str,
        file_content: bytes,
        user_id: int,
    ) -> DocumentUploadResponse:
        is_valid, error_msg = self.processor.validate_file(filename, len(file_content))
        if not is_valid:
            raise ValueError(error_msg)

        file_type = filename.rsplit(".", 1)[-1].lower()

        file_path = await self.processor.save_file(file_content, filename)

        document = Document(
            filename=filename,
            file_path=file_path,
            file_size=len(file_content),
            file_type=file_type,
            uploaded_by=user_id,
            status="processing",
            total_chunks=0,
        )
        self.db.add(document)
        await self.db.flush()

        try:
            text = await self.processor.extract_text(file_path, file_type)

            if not text:
                document.status = "error"
                await self.db.commit()
                raise ValueError("Could not extract text from file")

            chunks = self.processor.chunk_text(
                text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP
            )

            total_chunks = 0
            for chunk_data in chunks:
                embedding = await self.openrouter.generate_embedding(chunk_data["content"])

                if embedding:
                    chunk = DocumentChunk(
                        document_id=document.id,
                        chunk_index=chunk_data["index"],
                        content=chunk_data["content"],
                        embedding=embedding,
                        page_number=chunk_data.get("page_number"),
                    )
                    self.db.add(chunk)
                    total_chunks += 1

            document.total_chunks = total_chunks
            document.status = "completed"
            await self.db.commit()

            return DocumentUploadResponse(
                document_id=document.id,
                filename=filename,
                status="completed",
                total_chunks=total_chunks,
                message="Document uploaded and processed successfully",
            )

        except Exception as e:
            document.status = "error"
            await self.db.commit()
            raise e

    async def list_documents(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> DocumentListResponse:
        result = await self.db.execute(
            select(Document)
            .where(Document.uploaded_by == user_id)
            .order_by(Document.uploaded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        documents = result.scalars().all()

        count_result = await self.db.execute(
            select(Document).where(Document.uploaded_by == user_id)
        )
        total = len(count_result.scalars().all())

        return DocumentListResponse(
            total=total,
            items=[DocumentResponse.model_validate(d) for d in documents],
        )

    async def get_document(
        self,
        document_id: int,
        user_id: int,
    ) -> Optional[DocumentDetailResponse]:
        result = await self.db.execute(
            select(Document)
            .where(Document.id == document_id, Document.uploaded_by == user_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            return None

        return DocumentDetailResponse.model_validate(document)

    async def delete_document(self, document_id: int, user_id: int) -> bool:
        result = await self.db.execute(
            select(Document)
            .where(Document.id == document_id, Document.uploaded_by == user_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            return False

        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        await self.db.delete(document)
        await self.db.commit()

        return True
