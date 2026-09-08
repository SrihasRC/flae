"""Fact Knowledge Layer API main application module."""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("Starting Fact-Ledger Engine...")

    # 1. Initialize database tables
    await init_db()
    logger.info("Database tables initialized")

    # 2. Check ChromaDB connectivity (HttpClient or PersistentClient fallback)
    try:
        from app.services.vector_store import VectorStoreService

        vs = VectorStoreService()
        vs.client.heartbeat()
        if vs.client_type == "persistent":
            logger.info(f"ChromaDB ready (PersistentClient at {settings.CHROMA_PERSISTENT_PATH})")
        else:
            logger.info(f"ChromaDB connected at {settings.CHROMA_HOST}:{settings.CHROMA_PORT}")
    except Exception as e:
        logger.warning(
            f"ChromaDB not reachable at startup: {e}. Vector operations will fail until ChromaDB is available."
        )

    # 3. Ensure upload directory exists
    os.makedirs("uploads", exist_ok=True)
    logger.info("Upload directory ready")

    yield  # Application runs here

    # --- Shutdown ---
    logger.info("Shutting down Fact-Ledger Engine...")


app = FastAPI(
    title="Fact Knowledge Layer API",
    description="Epistemic Fact-Ledger with Arbitration Engine — Atomic Fact Extraction and Cross-Document Arbitration",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API v1 routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """Check API, database, and vector store connectivity."""
    db_status = "unknown"
    chroma_status = "unknown"

    # DB check
    try:
        from sqlalchemy import text

        from app.core.database import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # ChromaDB check
    try:
        from app.services.vector_store import VectorStoreService

        vs = VectorStoreService()
        vs.client.heartbeat()
        chroma_status = "connected"
    except Exception:
        chroma_status = "unavailable"

    return {
        "status": "healthy",
        "service": "fact-ledger-engine",
        "version": "0.1.0",
        "database": db_status,
        "vector_store": chroma_status,
    }
