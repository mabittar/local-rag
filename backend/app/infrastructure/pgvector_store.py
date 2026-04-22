import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk

logger = logging.getLogger(__name__)


class PGVectorStore:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[dict]:
        try:
            query = (
                select(
                    DocumentChunk.id,
                    DocumentChunk.document_id,
                    DocumentChunk.chunk_index,
                    DocumentChunk.content,
                    DocumentChunk.page_number,
                    DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
                )
                .order_by("distance")
                .limit(top_k)
            )

            result = await self.db.execute(query)
            rows = result.all()
            
            chunks = []
            for row in rows:
                chunks.append({
                    "id": str(row.id),
                    "document_id": row.document_id,
                    "chunk_index": row.chunk_index,
                    "content": row.content,
                    "page_number": row.page_number,
                    "similarity": 1.0 - float(row.distance),
                })

            return chunks

        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []

    async def get_chunk_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        from uuid import UUID

        try:
            result = await self.db.execute(
                select(DocumentChunk).where(DocumentChunk.id == UUID(chunk_id))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching chunk: {e}")
            return None
