from typing import AsyncGenerator, List

from app.infrastructure.openrouter import OpenRouterClient
from app.infrastructure.pgvector_store import PGVectorStore


class RAGService:
    def __init__(self, vector_store: PGVectorStore, openrouter: OpenRouterClient):
        self.vector_store = vector_store
        self.openrouter = openrouter

    async def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
    ) -> tuple[List[dict], str]:
        query_embedding = await self.openrouter.generate_embedding(query)

        if not query_embedding:
            return [], ""

        chunks = await self.vector_store.similarity_search(query_embedding, top_k)

        if not chunks:
            return [], ""

        context = self._build_context(chunks)
        return chunks, context

    def _build_context(self, chunks: List[dict]) -> str:
        context_parts = []
        for i, chunk in enumerate(chunks):
            context_parts.append(
                f"[Document {i + 1}] {chunk['content'][:500]}..."
            )
        return "\n\n".join(context_parts)

    def _build_prompt(self, query: str, context: str) -> List[dict]:
        system_prompt = """Você é um assistente útil que responde com base nos documentos fornecidos.
Use o contexto abaixo para responder à pergunta do usuário.
Se a resposta não estiver no contexto, diga que não encontrou informações relevantes.
Cite as fontes quando apropriado."""

        user_message = f"""Contexto dos documentos:
{context}

Pergunta do usuário:
{query}"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

    async def stream_chat_response(
        self,
        query: str,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        messages = self._build_prompt(query, context)

        async for token in self.openrouter.generate_chat_stream(
            messages, temperature, max_tokens
        ):
            yield token
