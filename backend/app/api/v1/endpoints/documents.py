"""FastAPI router endpoints for Document upload, status polling, and lifecycle."""

import logging
from pathlib import Path
from typing import Optional
import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)

from app.core.database import AsyncSessionLocal
from app.dependencies import (
    get_document_repo,
    get_fact_repo,
    get_vector_store,
    get_workspace_repo,
)
from app.repositories.arbitration_repository import ArbitrationRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.fact_repository import FactRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.document import (
    DocumentListResponse,
    DocumentRead,
    DocumentUploadResponse,
    IngestionJobStatus,
)
from app.services.arbitration_service import ArbitrationService
from app.services.embedding_service import EmbeddingService
from app.services.extraction_service import ExtractionService
from app.services.local_extraction import LocalExtractionService
from app.services.pdf_parser import extract_pdf_metadata, parse_pdf
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Documents"])

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB limit as specified in API Blueprint


async def run_ingestion_pipeline(
    document_id: uuid.UUID,
    workspace_id: uuid.UUID,
    file_path: str,
    doc_repo: Optional[DocumentRepository] = None,
    fact_repo: Optional[FactRepository] = None,
    arb_repo: Optional[ArbitrationRepository] = None,
    extraction_svc: Optional[ExtractionService] = None,
    embedding_svc: Optional[EmbeddingService] = None,
    vector_store: Optional[VectorStoreService] = None,
    arbitration_svc: Optional[ArbitrationService] = None,
) -> None:
    """Asynchronous background pipeline for PDF ingestion, extraction, embedding, and arbitration.

    Executes in a dedicated async DB session to prevent premature session closure.
    """
    if doc_repo is None:
        async with AsyncSessionLocal() as session:
            try:
                local_doc_repo = DocumentRepository(session)
                local_fact_repo = FactRepository(session)
                local_arb_repo = ArbitrationRepository(session)
                local_extraction_svc = extraction_svc or LocalExtractionService()
                local_embedding_svc = embedding_svc or EmbeddingService()
                local_vector_store = vector_store or VectorStoreService()
                local_arbitration_svc = arbitration_svc or ArbitrationService(
                    local_embedding_svc, local_vector_store, local_fact_repo
                )

                # Ensure document record exists before proceeding
                doc = await local_doc_repo.get_by_id(document_id)
                if doc is None:
                    logger.warning("Document %s not found immediately in session; polling...", document_id)
                    for _ in range(10):
                        await asyncio.sleep(0.1)
                        doc = await local_doc_repo.get_by_id(document_id)
                        if doc is not None:
                            break
                    if doc is None:
                        logger.error("Document %s not found in database; aborting pipeline", document_id)
                        return

                await local_doc_repo.update_status(document_id, "processing")
                await session.commit()

                # 1. Read file bytes
                file_bytes = Path(file_path).read_bytes()

                # 2. Parse PDF
                blocks, visual_pages = parse_pdf(file_bytes, Path(file_path).name)
                logger.info(
                    "PDF parsing complete (%d blocks, %d visual pages) for %s",
                    len(blocks),
                    len(visual_pages),
                    document_id,
                )

                # 3. Extract facts
                facts = await local_extraction_svc.extract_facts(
                    blocks=blocks,
                    document_id=document_id,
                    workspace_id=workspace_id,
                    visual_pages=visual_pages,
                    file_bytes=file_bytes,
                    filename=Path(file_path).name,
                )
                logger.info(
                    "Fact extraction complete (%d facts) for %s",
                    len(facts),
                    document_id,
                )

                # 4. Store facts in DB
                stored_facts = await local_fact_repo.create_bulk(facts)
                await session.commit()

                # 5. Embed facts into vector store
                for fact in stored_facts:
                    embedding = await local_embedding_svc.embed_fact_anchor(
                        fact.subject, fact.attribute
                    )
                    local_vector_store.upsert_fact(
                        workspace_id=workspace_id,
                        fact_id=str(fact.id),
                        embedding=embedding,
                        metadata={
                            "document_id": str(fact.document_id),
                            "subject": fact.subject,
                            "attribute": fact.attribute,
                        },
                    )

                # 6. Arbitration skipped (LLM quota exhausted — run later via POST /arbitration/run)
                arb_results: list[dict] = []

                # 8. Update status to complete
                await local_doc_repo.update_status(
                    document_id, "complete", facts_extracted=len(facts)
                )
                await session.commit()
                logger.info(
                    "Document ingestion complete: %s, %d facts, %d arbitrations",
                    document_id,
                    len(facts),
                    len(arb_results),
                )
            except Exception as e:
                logger.error(
                    "Pipeline failure for %s: %s", document_id, e, exc_info=True
                )
                try:
                    await session.rollback()
                    local_doc_repo = DocumentRepository(session)
                    await local_doc_repo.update_status(
                        document_id, "failed", error=str(e)
                    )
                    await session.commit()
                except Exception as rollback_err:
                    logger.error(
                        "Failed to update document failure status for %s: %s",
                        document_id,
                        rollback_err,
                        exc_info=True,
                    )
    else:
        try:
            await doc_repo.update_status(document_id, "processing")
            file_bytes = Path(file_path).read_bytes()
            blocks, visual_pages = parse_pdf(file_bytes, Path(file_path).name)
            logger.info(
                "PDF parsing complete (%d blocks, %d visual pages) for %s",
                len(blocks),
                len(visual_pages),
                document_id,
            )

            local_ext = extraction_svc or LocalExtractionService()
            facts = await local_ext.extract_facts(
                blocks=blocks,
                document_id=document_id,
                workspace_id=workspace_id,
                visual_pages=visual_pages,
                file_bytes=file_bytes,
                filename=Path(file_path).name,
            )
            logger.info("Fact extraction complete (%d facts)", len(facts))

            stored_facts = await fact_repo.create_bulk(facts)
            local_emb = embedding_svc or EmbeddingService()
            local_vec = vector_store or VectorStoreService()

            for fact in stored_facts:
                embedding = await local_emb.embed_fact_anchor(
                    fact.subject, fact.attribute
                )
                local_vec.upsert_fact(
                    workspace_id=workspace_id,
                    fact_id=str(fact.id),
                    embedding=embedding,
                    metadata={
                        "document_id": str(fact.document_id),
                        "subject": fact.subject,
                        "attribute": fact.attribute,
                    },
                )

            # Arbitration skipped by default (LLM quota exhausted — run later via POST /arbitration/run)
            arb_results = []
            if arbitration_svc is not None:
                arb_results = await arbitration_svc.run_arbitration_for_workspace(
                    workspace_id, new_document_id=document_id
                )
                if arb_results and arb_repo:
                    await arb_repo.create_bulk(
                        [
                            dict(result) | {"workspace_id": str(workspace_id)}
                            for result in arb_results
                        ]
                    )

            await doc_repo.update_status(
                document_id, "complete", facts_extracted=len(facts)
            )
            logger.info("Document ingestion complete: %s", document_id)
        except Exception as e:
            logger.error("Pipeline failure for %s: %s", document_id, e, exc_info=True)
            await doc_repo.update_status(document_id, "failed", error=str(e))


@router.post(
    "/{workspace_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload PDF and trigger ingestion pipeline",
)
async def upload_document(
    workspace_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    document_repo: DocumentRepository = Depends(get_document_repo),
) -> DocumentUploadResponse:
    """Upload a PDF document, store it on disk, and dispatch the background ingestion pipeline."""
    logger.info(
        "Document ingestion started for file '%s' in workspace '%s'",
        file.filename,
        workspace_id,
    )

    ws = await workspace_repo.get_by_id(workspace_id)
    if ws is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )

    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF documents are supported for ingestion",
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB",
        )

    # Extract metadata including physical page count
    meta = extract_pdf_metadata(file_bytes)
    page_count = int(meta.get("page_count", 0))

    # Save to backend/uploads/{workspace_id}/{filename}
    backend_root = Path(__file__).resolve().parents[4]
    upload_dir = backend_root / "uploads" / str(workspace_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    target_path = upload_dir / filename
    target_path.write_bytes(file_bytes)

    # Create document record with status "pending"
    doc_id = uuid.uuid4()
    doc = await document_repo.create(
        {
            "id": doc_id,
            "workspace_id": workspace_id,
            "filename": filename,
            "file_path": str(target_path),
            "page_count": page_count,
            "status": "pending",
            "facts_extracted": 0,
        }
    )
    # Explicitly commit so background task running in an independent session can see the record
    await document_repo.db.commit()

    # Dispatch ingestion pipeline to run in the background
    background_tasks.add_task(
        run_ingestion_pipeline,
        document_id=doc.id,
        workspace_id=workspace_id,
        file_path=str(target_path),
    )

    return DocumentUploadResponse(
        document_id=doc.id,
        filename=doc.filename,
        workspace_id=doc.workspace_id,
        status="pending",
        uploaded_at=doc.uploaded_at,
    )


@router.get(
    "/{workspace_id}/documents",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all documents in a workspace",
)
async def list_documents(
    workspace_id: uuid.UUID,
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    document_repo: DocumentRepository = Depends(get_document_repo),
) -> DocumentListResponse:
    """Retrieve all documents belonging to a workspace."""
    ws = await workspace_repo.get_by_id(workspace_id)
    if ws is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )

    docs = await document_repo.list_by_workspace(workspace_id)
    return DocumentListResponse(
        documents=[DocumentRead.model_validate(doc) for doc in docs]
    )


@router.get(
    "/{workspace_id}/documents/{document_id}/status",
    response_model=IngestionJobStatus,
    status_code=status.HTTP_200_OK,
    summary="Poll ingestion pipeline status",
)
async def get_document_status(
    workspace_id: uuid.UUID,
    document_id: uuid.UUID,
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    document_repo: DocumentRepository = Depends(get_document_repo),
) -> IngestionJobStatus:
    """Poll the ingestion pipeline execution status for a specific document."""
    ws = await workspace_repo.get_by_id(workspace_id)
    if ws is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )

    doc = await document_repo.get_by_id(document_id)
    if doc is None or doc.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found in workspace '{workspace_id}'",
        )

    return IngestionJobStatus(
        document_id=doc.id,
        status=doc.status,
        facts_extracted=doc.facts_extracted,
        error=doc.error,
    )


@router.delete(
    "/{workspace_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document, facts, and vector embeddings",
)
async def delete_document(
    workspace_id: uuid.UUID,
    document_id: uuid.UUID,
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    document_repo: DocumentRepository = Depends(get_document_repo),
    fact_repo: FactRepository = Depends(get_fact_repo),
    vector_store: VectorStoreService = Depends(get_vector_store),
) -> Response:
    """Delete a document, purge its extracted facts, and remove its vector embeddings."""
    ws = await workspace_repo.get_by_id(workspace_id)
    if ws is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )

    doc = await document_repo.get_by_id(document_id)
    if doc is None or doc.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found in workspace '{workspace_id}'",
        )

    # Delete indexed embeddings from vector store
    vector_store.delete_by_document(workspace_id, document_id)

    # Delete atomic facts from DB
    await fact_repo.delete_by_document(document_id)

    # Delete document record
    await document_repo.delete(document_id)

    # Delete physical file from filesystem if present
    if doc.file_path:
        p = Path(doc.file_path)
        if p.exists():
            p.unlink(missing_ok=True)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
