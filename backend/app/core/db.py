"""Database configuration and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

# from sqlmodel import SQLModel


# Create async engine
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.ENVIRONMENT == "local",
    future=True,
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    """
    async with AsyncSessionLocal() as session:
        yield session


# async def init_db() -> None:
#     """
#     Initialize database.

#     Note: In production, use Alembic migrations instead.
#     This is only for development/testing.
#     """
#     async with engine.begin() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)
