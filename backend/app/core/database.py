from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings
from app.core.security import get_password_hash

# Create async engine
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_size=20,
    max_overflow=0,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables and seed data."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    await seed_data()


async def seed_data() -> None:
    """Seed initial data if not exists."""
    from app.models.user import User

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(User).where(User.username == "localuser")
            )
            existing_user = result.scalar_one_or_none()

            if not existing_user:
                seed_user = User(
                    username="localuser",
                    hashed_password=get_password_hash("localuser123"),
                    role="admin",
                )
                session.add(seed_user)
                await session.commit()
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db() -> None:
    """Close database connections."""
    await async_engine.dispose()
