import logging
from collections.abc import AsyncGenerator
from typing import Any

import asyncpg
from asyncpg.exceptions import InvalidCatalogNameError
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Declarative base class for all SQLAlchemy ORM models."""

    pass


engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def _create_database_if_not_exists(target_db: str, url: Any) -> None:
    """Connect to default maintenance database and create target database if absent."""
    kwargs: dict[str, Any] = {}
    if url.host:
        kwargs["host"] = url.host
    if url.port:
        kwargs["port"] = url.port
    if url.username:
        kwargs["user"] = url.username
    if url.password:
        kwargs["password"] = url.password

    maintenance_db = "postgres"
    conn = None
    try:
        conn = await asyncpg.connect(**kwargs, database=maintenance_db)
    except Exception:
        maintenance_db = "template1"
        conn = await asyncpg.connect(**kwargs, database=maintenance_db)

    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", target_db
        )
        if not exists:
            logger.info(
                "Database '%s' not found. Creating database via '%s'...",
                target_db,
                maintenance_db,
            )
            await conn.execute(f'CREATE DATABASE "{target_db}"')
            logger.info("Database '%s' created successfully.", target_db)
    finally:
        await conn.close()


async def init_db() -> None:
    """Initialize database tables defined on Base metadata."""
    from app.models import workspace, document, fact, arbitration  # noqa: F401

    logger.info("Initializing database tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as exc:
        is_catalog_error = (
            isinstance(exc, InvalidCatalogNameError)
            or isinstance(getattr(exc, "orig", None), InvalidCatalogNameError)
            or "does not exist" in str(exc).lower()
        )
        if is_catalog_error:
            url = make_url(settings.DATABASE_URL)
            target_db = url.database or "fact_ledger"
            logger.warning(
                "Database '%s' does not exist (%s). Attempting auto-creation...",
                target_db,
                exc,
            )
            await _create_database_if_not_exists(target_db, url)
            await engine.dispose()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized successfully after database creation.")
        else:
            logger.error("Failed to initialize database: %s", exc)
            raise
