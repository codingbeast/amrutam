from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config.settings import settings

# --------------------------------------
# DATABASE URL
# --------------------------------------
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.DB_NAME}"
)

class Base(DeclarativeBase):
    pass
# --------------------------------------
# ENGINE
# --------------------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=1800,
)

# --------------------------------------
# SESSION FACTORY
# --------------------------------------
async_session_factory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# --------------------------------------
# FASTAPI DEPENDENCY
# --------------------------------------
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# --------------------------------------
# SIMPLE CONNECT TEST
# --------------------------------------
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(lambda x: None)
    print("DB connection OK")

# Sync engine for Alembic
def get_sync_engine():
    from sqlalchemy import create_engine
    SYNC_URL = DATABASE_URL.replace("+asyncpg", "")
    return create_engine(SYNC_URL)
