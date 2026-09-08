"""FastAPI router endpoints for Workspace management."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import (
    get_document_repo,
    get_vector_store,
    get_workspace_repo,
)
from app.repositories.document_repository import DocumentRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceListResponse,
    WorkspaceRead,
)
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Workspaces"])


@router.post(
    "",
    response_model=WorkspaceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workspace",
)
@router.post(
    "/",
    response_model=WorkspaceRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_workspace(
    payload: WorkspaceCreate,
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
) -> WorkspaceRead:
    """Create a new domain workspace partition."""
    existing = await workspace_repo.get_by_name(payload.name)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Workspace name '{payload.name}' already exists",
        )

    workspace = await workspace_repo.create(payload.model_dump())
    return WorkspaceRead(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        created_at=workspace.created_at,
        document_count=0,
    )


@router.get(
    "",
    response_model=WorkspaceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all workspaces",
)
@router.get(
    "/",
    response_model=WorkspaceListResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def list_workspaces(
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    document_repo: DocumentRepository = Depends(get_document_repo),
) -> WorkspaceListResponse:
    """Retrieve all workspaces with their associated document counts."""
    workspaces = await workspace_repo.list_all()
    results: list[WorkspaceRead] = []
    for ws in workspaces:
        doc_count = await document_repo.count_by_workspace(ws.id)
        results.append(
            WorkspaceRead(
                id=ws.id,
                name=ws.name,
                description=ws.description,
                created_at=ws.created_at,
                document_count=doc_count,
            )
        )
    return WorkspaceListResponse(workspaces=results)


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceRead,
    status_code=status.HTTP_200_OK,
    summary="Get workspace by ID",
)
async def get_workspace(
    workspace_id: uuid.UUID,
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    document_repo: DocumentRepository = Depends(get_document_repo),
) -> WorkspaceRead:
    """Retrieve a single workspace by its unique identifier."""
    ws = await workspace_repo.get_by_id(workspace_id)
    if ws is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )

    doc_count = await document_repo.count_by_workspace(ws.id)
    return WorkspaceRead(
        id=ws.id,
        name=ws.name,
        description=ws.description,
        created_at=ws.created_at,
        document_count=doc_count,
    )


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workspace and cascade vector collections",
)
async def delete_workspace(
    workspace_id: uuid.UUID,
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    vector_store: VectorStoreService = Depends(get_vector_store),
) -> Response:
    """Delete a workspace and cascade delete its ChromaDB collection."""
    ws = await workspace_repo.get_by_id(workspace_id)
    if ws is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )

    await workspace_repo.delete(workspace_id)
    vector_store.delete_collection(workspace_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
