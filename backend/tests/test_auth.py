import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.user import User


class TestAuth:
    """Test authentication business rules."""
    
    async def test_login_success_valid_credentials(
        self, client: AsyncClient, test_user: User
    ):
        """Test: Login with valid credentials returns JWT token."""
        # Arrange
        credentials = {
            "username": "testuser",
            "password": "testpass123",
        }
        
        # Act
        response = await client.post("/api/auth/login", json=credentials)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    async def test_login_failure_invalid_password(
        self, client: AsyncClient, test_user: User
    ):
        """Test: Login with invalid password returns 401."""
        # Arrange
        credentials = {
            "username": "testuser",
            "password": "wrongpassword",
        }
        
        # Act
        response = await client.post("/api/auth/login", json=credentials)
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Invalid credentials" in data["detail"]
    
    async def test_login_failure_invalid_username(
        self, client: AsyncClient
    ):
        """Test: Login with non-existent username returns 401."""
        # Arrange
        credentials = {
            "username": "nonexistent",
            "password": "anypassword",
        }
        
        # Act
        response = await client.post("/api/auth/login", json=credentials)
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    async def test_password_hashing(self):
        """Test: Password hashing works correctly."""
        from app.core.security import get_password_hash
        
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
