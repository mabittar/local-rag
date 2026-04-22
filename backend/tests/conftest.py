import asyncio
import os
import tempfile
from typing import AsyncGenerator, Optional

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

# Set test environment before importing app
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DEBUG"] = "true"
os.environ["OPENROUTER_API_KEY"] = "test-key"
os.environ["UPLOAD_DIR"] = "/tmp/test_uploads"

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User

# Test database configuration
# Option 1: SQLite in-memory (fast, no event loop issues)
# Option 2: PostgreSQL test database (required for pgvector tests)
USE_SQLITE = os.getenv("TEST_USE_SQLITE", "true").lower() == "true"

if USE_SQLITE:
    # SQLite in-memory with async support
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
else:
    # PostgreSQL test database
    TEST_DATABASE_URL = settings.DATABASE_URL
    if settings.DATABASE_URL.endswith('/localrag'):
        TEST_DATABASE_URL = settings.DATABASE_URL[:-len('localrag')] + 'localrag_test'


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    # For SQLite in-memory, no cleanup needed (destroyed automatically)
    if not USE_SQLITE:
        # Drop all tables for PostgreSQL
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create fresh database session for each test with transaction rollback."""
    # Create session factory
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session() as session:
        yield session
        # Rollback any changes after test
        await session.rollback()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create test user."""
    from sqlalchemy import select
    
    # Check if user exists
    result = await db_session.execute(
        select(User).where(User.username == "testuser")
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return existing
    
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        role="admin",
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    from app.api.deps import get_db
    from main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers with valid token."""
    from app.core.security import create_access_token

    token = create_access_token(
        data={"sub": str(test_user.id), "username": test_user.username}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def test_upload_dir():
    """Create temporary upload directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["UPLOAD_DIR"] = tmpdir
        yield tmpdir


# Skip markers for tests requiring PostgreSQL/pgvector
requires_postgres = pytest.mark.skipif(
    USE_SQLITE,
    reason="Test requires PostgreSQL with pgvector support"
)
