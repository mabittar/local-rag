from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class TestChat:
    """Test chat business rules."""
    
    async def test_create_session_success(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession, test_user: User
    ):
        """Test: Create chat session returns 200 with session_id."""
        # Arrange
        data = {"title": "Test Session"}
        
        # Act
        response = await client.post(
            "/api/chat/sessions",
            headers=auth_headers,
            json=data,
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "id" in result
        assert result["title"] == "Test Session"
        assert "created_at" in result
    
    async def test_list_sessions_success(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test: List sessions returns user sessions."""
        # Act
        response = await client.get(
            "/api/chat/sessions",
            headers=auth_headers,
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "items" in result
        assert "total" in result
        assert isinstance(result["items"], list)
    
    async def test_get_messages_invalid_session(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test: Get messages for invalid session returns 404."""
        # Act
        response = await client.get(
            "/api/chat/sessions/99999/messages",
            headers=auth_headers,
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    async def test_delete_session_invalid_id(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test: Delete non-existent session returns 404."""
        # Act
        response = await client.delete(
            "/api/chat/sessions/99999",
            headers=auth_headers,
        )
        
        # Assert
        assert response.status_code == 404
    
    async def test_stream_chat_invalid_session(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test: Stream chat with invalid session returns 404.
        
        Note: The chat stream endpoint is GET with query parameters (SSE),
        not POST with JSON body.
        """
        # Act - GET request with query parameters
        response = await client.get(
            "/api/chat/stream?session_id=99999&message=Test%20message",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Chat session not found" in data.get("detail", "")
    
    async def test_chat_session_lifecycle(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession, test_user: User
    ):
        """Test: Full lifecycle - create, verify, delete session."""
        # Create
        create_response = await client.post(
            "/api/chat/sessions",
            headers=auth_headers,
            json={"title": "Lifecycle Test"},
        )
        assert create_response.status_code == 200
        session_id = create_response.json()["id"]
        
        # List and verify
        list_response = await client.get(
            "/api/chat/sessions",
            headers=auth_headers,
        )
        assert list_response.status_code == 200
        sessions = list_response.json()["items"]
        assert any(s["id"] == session_id for s in sessions)
        
        # Delete
        delete_response = await client.delete(
            f"/api/chat/sessions/{session_id}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 204
        
        # Verify deleted
        get_response = await client.get(
            "/api/chat/sessions",
            headers=auth_headers,
        )
        sessions_after = get_response.json()["items"]
        assert not any(s["id"] == session_id for s in sessions_after)
