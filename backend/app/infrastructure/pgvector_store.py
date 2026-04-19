import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector

from app.core.config import settings
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
        from sqlalchemy import text

        try:
            query = text("""
                SELECT 
                    dc.id,
                    dc.document_id,
                    dc.chunk_index,
                    dc.content,
                    dc.page_number,
                    dc.embedding <=> :embedding as distance
                FROM document_chunks dc
                ORDER BY dc.embedding <=> :embedding
                LIMIT :limit
            """)

            result = await self.db.execute(
                query,
                {
                    "embedding": query_embedding,
                    "limit": top_k,
                },
            )

            rows = result.fetchall()
            chunks = []
            for row in rows:
                chunks.append({
                    "id": str(row[0]),
                    "document_id": row[1],
                    "chunk_index": row[2],
                    "content": row[3],
                    "page_number": row[4],
                    "similarity": 1.0 - float(row[5]),
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
