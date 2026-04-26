import os
import re
from typing import List, Tuple
from uuid import uuid4

import aiofiles

from app.core.config import settings


class DocumentProcessor:
    ALLOWED_EXTENSIONS = {"pdf", "txt", "md", "docx", "xlsx", "pptx"}
    MAX_FILE_SIZE = 5242880  # 5Mb

    @staticmethod
    def secure_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal attacks."""
        filename = filename.replace("\\", "/")
        filename = os.path.basename(filename)
        filename = re.sub(r"^\.+/*", "", filename)
        filename = re.sub(r"[^\w.\-]", "_", filename)
        if not filename or filename == "." or filename == "..":
            filename = "unnamed_file"
        return filename

    @staticmethod
    def validate_file(filename: str, content_length: int) -> Tuple[bool, str]:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        if ext not in DocumentProcessor.ALLOWED_EXTENSIONS:
            return (
                False,
                f"File type not supported. Allowed: {', '.join(DocumentProcessor.ALLOWED_EXTENSIONS)}",
            )

        if content_length > DocumentProcessor.MAX_FILE_SIZE:
            return False, "File size exceeds maximum limit of 5MB"

        return True, ""

    @staticmethod
    async def save_file(file_content: bytes, filename: str) -> str:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        safe_filename = f"{uuid4()}_{filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)

        return file_path

    @staticmethod
    async def extract_text(file_path: str, file_type: str) -> str:
        if file_type in ["pdf", "docx", "xlsx", "pptx"]:
            return await DocumentProcessor._convert_to_markdown(file_path)
        elif file_type in ["txt", "md"]:
            return await DocumentProcessor._extract_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    async def _convert_to_markdown(file_path: str) -> str:
        try:
            import markitdown
            from openai import OpenAI

            md = markitdown.MarkItDown(
                enable_plugins=True,
                enable_extensions=True,
                llm_client=OpenAI(
                    base_url="http://localhost:11434/v1",
                    api_key="",
                ),
                llm_model="llama3.2",
            )
            text = md.convert_file(file_path)
            return text
        except Exception:
            return ""

    @staticmethod
    async def _extract_text_file(file_path: str) -> str:
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                return await f.read()
        except Exception as e:
            raise e

    @staticmethod
    def chunk_text(text: str, chunk_size: int, overlap: int) -> List[dict]:
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]

            chunks.append(
                {
                    "index": chunk_index,
                    "content": chunk,
                    "page_number": None,
                }
            )

            start = end - overlap if end < len(text) else end
            chunk_index += 1

        return chunks
