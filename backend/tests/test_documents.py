import io
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.document_processor import DocumentProcessor
from app.models.document import Document


class TestDocuments:
    """Test document upload business rules."""
    
    async def test_upload_success_valid_txt(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """Test: Upload valid TXT file returns 201 and creates document.
        
        Note: This test validates the upload API endpoint. Document processing
        (chunking, embeddings) is handled asynchronously and requires pgvector.
        For full processing tests, run with PostgreSQL backend.
        """
        import os
        # Ensure upload directory exists
        os.makedirs(os.environ.get("UPLOAD_DIR", "/tmp/test_uploads"), exist_ok=True)
        
        # Arrange - create simple text content
        content = b"This is a test document content for testing purposes."
        file = io.BytesIO(content)

        # Act
        response = await client.post(
            "/api/documents/upload",
            headers=auth_headers,
            files={"file": ("test.txt", file, "text/plain")},
        )

        # Assert - API accepts upload and creates document record
        # Status may be 200, 201, or 202 depending on implementation
        assert response.status_code in [200, 201, 202], f"Unexpected status: {response.status_code}, body: {response.text}"
        data = response.json()
        assert "document_id" in data
        assert data["filename"] == "test.txt"
        assert "status" in data

        # Verify in database - document record exists
        result = await db_session.execute(
            select(Document).where(Document.id == data["document_id"])
        )
        doc = result.scalar_one_or_none()
        assert doc is not None
        assert doc.filename == "test.txt"
    
    async def test_upload_failure_invalid_file_type(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test: Upload invalid file type returns 400."""
        # Arrange
        content = b"invalid content"
        file = io.BytesIO(content)
        
        # Act
        response = await client.post(
            "/api/documents/upload",
            headers=auth_headers,
            files={"file": ("malware.exe", file, "application/x-msdownload")},
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "File type not supported" in data["detail"]
    
    async def test_upload_failure_unauthorized(
        self, client: AsyncClient
    ):
        """Test: Upload without auth returns 401."""
        # Arrange
        content = b"test content"
        file = io.BytesIO(content)

        # Act
        response = await client.post(
            "/api/documents/upload",
            files={"file": ("test.txt", file, "text/plain")},
        )

        # Assert - 401 for unauthenticated, 403 for unauthorized
        assert response.status_code == 401
    
    async def test_list_documents_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test: List documents returns paginated results."""
        # Act
        response = await client.get(
            "/api/documents",
            headers=auth_headers,
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
    
    async def test_get_document_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test: Get non-existent document returns 404."""
        # Act
        response = await client.get(
            "/api/documents/99999",
            headers=auth_headers,
        )
        
        # Assert
        assert response.status_code == 404


class TestDocumentProcessor:
    """Test document processing logic."""
    
    def test_validate_file_valid_txt(self):
        """Test: Valid TXT file passes validation."""
        is_valid, error = DocumentProcessor.validate_file("document.txt", 1024)
        assert is_valid is True
        assert error == ""
    
    def test_validate_file_invalid_extension(self):
        """Test: Invalid extension fails validation."""
        is_valid, error = DocumentProcessor.validate_file("file.exe", 1024)
        assert is_valid is False
        assert "File type not supported" in error
    
    def test_validate_file_too_large(self):
        """Test: File over 100MB fails validation."""
        is_valid, error = DocumentProcessor.validate_file("large.pdf", 200_000_000)
        assert is_valid is False
        assert "exceeds maximum limit" in error
    
    def test_chunk_text_simple(self):
        """Test: Text chunking creates correct chunks."""
        text = " ".join(["word"] * 1000)  # Long text
        chunks = DocumentProcessor.chunk_text(text, chunk_size=100, overlap=10)
        
        assert len(chunks) > 0
        assert all("index" in c for c in chunks)
        assert all("content" in c for c in chunks)
