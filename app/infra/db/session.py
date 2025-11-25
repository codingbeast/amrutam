import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import scoped_session

from app.core.config.settings import settings


# --------------------------------------
# DATABASE URL (from env variables)
# --------------------------------------
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.DB_NAME}"
)


# --------------------------------------
# CREATE ASYNC ENGINE (global)
# --------------------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DB_ECHO,  # Debug SQL logs
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,      # check stale connections
    pool_recycle=1800,       # recycle every 30 mins
)


# --------------------------------------
# ASYNC SESSION FACTORY
# --------------------------------------
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


# --------------------------------------
# FASTAPI DEPENDENCY — DB SESSION
# --------------------------------------
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = AsyncSessionFactory()

    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# --------------------------------------
# INIT DB (used in app startup event)
# --------------------------------------
async def init_db():
    """
    Used in FastAPI startup event.
    Ensures the database connection can be established.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda x: None)  # simple ping
        print("DB connection established.")
    except Exception as e:
        print("DB connection failed:", e)
        raise


# Optional for Alembic or CLI scripts
def get_sync_engine():
    """Return a sync engine for Alembic migrations (optional)."""
    from sqlalchemy import create_engine

    SYNC_DB_URL = DATABASE_URL.replace("+asyncpg", "")
    return create_engine(SYNC_DB_URL)
