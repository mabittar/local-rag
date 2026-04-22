import asyncio
import json
import logging
from typing import AsyncGenerator, List, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        self.chat_model = settings.OPENROUTER_MODEL
        self.embedding_model = settings.OPENROUTER_EMBEDDING_MODEL

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException)),
        before_sleep=lambda retry_state: logger.warning(
            f"Retrying embedding generation after error: {retry_state.outcome.exception()}"
        ),
    )
    async def _generate_embedding_request(self, text: str) -> List[float]:
        """Internal method with retry logic."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.embedding_model,
            "input": text,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        if not self.api_key:
            logger.error("OpenRouter API key not configured")
            return None

        try:
            return await self._generate_embedding_request(text)
        except Exception as e:
            logger.error(f"Error generating embedding after retries: {e}")
            return None

    async def generate_chat_stream(
        self,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            logger.error("OpenRouter API key not configured")
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.chat_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        max_retries = 3
        retry_delay = 2  # segundos iniciais

        for attempt in range(max_retries):
            async with httpx.AsyncClient() as client:
                try:
                    async with client.stream(
                        "POST",
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=120.0,
                    ) as response:
                        if response.status_code == 429:
                            if attempt < max_retries - 1:
                                wait_time = retry_delay * (2 ** attempt)
                                logger.warning(f"Rate limit hit (429). Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                raise Exception("Limite de requisições do OpenRouter atingido. Por favor, tente novamente em alguns minutos.")

                        if response.status_code >= 500:
                            if attempt < max_retries - 1:
                                wait_time = retry_delay * (2 ** attempt)
                                logger.warning(f"Server error ({response.status_code}). Retrying in {wait_time}s...")
                                await asyncio.sleep(wait_time)
                                continue

                        response.raise_for_status()
                        
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                
                                try:
                                    data_json = json.loads(data_str)
                                    content = data_json["choices"][0].get("delta", {}).get("content", "")
                                    if content:
                                        yield content
                                except Exception:
                                    continue
                        
                        return

                except (httpx.ConnectError, httpx.TimeoutException) as e:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"Connection error: {e}. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    raise Exception(f"Erro de conexão com a IA: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error in chat stream: {e}")
                    raise e
