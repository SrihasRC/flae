"""FastAPI dependency providers for repositories and services."""

from typing import Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.arbitration_repository import ArbitrationRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.fact_repository import FactRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.arbitration_service import ArbitrationService
from app.services.embedding_service import EmbeddingService
from app.services.extraction_service import ExtractionService
from app.services.pdf_parser import parse_pdf  # stateless, no class needed
from app.services.vector_store import VectorStoreService


def get_workspace_repo(db: AsyncSession = Depends(get_db)) -> WorkspaceRepository:
    """Provide a WorkspaceRepository instance scoped to the request DB session."""
    return WorkspaceRepository(db)


def get_document_repo(db: AsyncSession = Depends(get_db)) -> DocumentRepository:
    """Provide a DocumentRepository instance scoped to the request DB session."""
    return DocumentRepository(db)


def get_fact_repo(db: AsyncSession = Depends(get_db)) -> FactRepository:
    """Provide a FactRepository instance scoped to the request DB session."""
    return FactRepository(db)


def get_arbitration_repo(db: AsyncSession = Depends(get_db)) -> ArbitrationRepository:
    """Provide an ArbitrationRepository instance scoped to the request DB session."""
    return ArbitrationRepository(db)


def get_extraction_service() -> ExtractionService:
    """Provide an ExtractionService instance."""
    return ExtractionService()


def get_embedding_service() -> EmbeddingService:
    """Provide an EmbeddingService instance."""
    return EmbeddingService()


_vector_store_instance: Optional[VectorStoreService] = None


def get_vector_store() -> VectorStoreService:
    """Provide a cached singleton VectorStoreService instance."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStoreService()
    return _vector_store_instance


def get_arbitration_service(
    embedding_svc: EmbeddingService = Depends(get_embedding_service),
    vector_store: VectorStoreService = Depends(get_vector_store),
    fact_repo: FactRepository = Depends(get_fact_repo),
) -> ArbitrationService:
    """Provide an ArbitrationService instance wired with dependencies."""
    return ArbitrationService(embedding_svc, vector_store, fact_repo)
