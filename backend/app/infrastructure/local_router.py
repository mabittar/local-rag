from typing import AsyncGenerator, List
import ollama
from llama_index.embeddings.ollama import OllamaEmbedding


class LocalRouterLLM:
    def __init__(self):
        self.embed_model = OllamaEmbedding(
            model_name="all-minilm",
            base_url="http://localhost:11434",
            ollama_additional_kwargs={"rocm": True},
            embed_batch_size=16,
        )

    async def generate_embedding(self, text: str) -> List[float]:
        return await self.embed_model.aget_text_embedding(text)

    async def generate_chat_stream(
        self,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        stream = ollama.chat(
            model="llama3.2",
            messages=messages,
            stream=True,
        )

        for chunk in stream:
            yield chunk["message"]["content"]
