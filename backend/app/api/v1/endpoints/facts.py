"""FastAPI router endpoints for querying atomic facts ledger."""

import logging
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_fact_repo, get_workspace_repo
from app.repositories.fact_repository import FactRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.fact import FactListResponse, FactRead

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Facts"])


@router.get(
    "/{workspace_id}/facts",
    response_model=FactListResponse,
    status_code=status.HTTP_200_OK,
    summary="List facts in a workspace with optional filters",
)
async def list_facts(
    workspace_id: uuid.UUID,
    document_id: Optional[uuid.UUID] = Query(
        default=None, description="Filter facts by source document UUID"
    ),
    subject: Optional[str] = Query(
        default=None, description="Case-insensitive substring filter on subject"
    ),
    attribute: Optional[str] = Query(
        default=None, description="Case-insensitive substring filter on attribute"
    ),
    skip: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=50, ge=1, le=200, description="Max results per page"),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    fact_repo: FactRepository = Depends(get_fact_repo),
) -> FactListResponse:
    """Retrieve paginated atomic facts from the ledger for a specific workspace."""
    ws = await workspace_repo.get_by_id(workspace_id)
    if ws is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )

    facts = await fact_repo.list_by_workspace(
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
        document_id=document_id,
        subject=subject,
        attribute=attribute,
    )
    total = await fact_repo.count_by_workspace(
        workspace_id=workspace_id,
        document_id=document_id,
        subject=subject,
        attribute=attribute,
    )

    return FactListResponse(
        facts=[FactRead.model_validate(f) for f in facts],
        total=total,
    )


@router.get(
    "/{workspace_id}/facts/{fact_id}",
    response_model=FactRead,
    status_code=status.HTTP_200_OK,
    summary="Get single fact by ID",
)
async def get_fact(
    workspace_id: uuid.UUID,
    fact_id: uuid.UUID,
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    fact_repo: FactRepository = Depends(get_fact_repo),
) -> FactRead:
    """Retrieve a single atomic fact from the ledger by its ID."""
    ws = await workspace_repo.get_by_id(workspace_id)
    if ws is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )

    fact = await fact_repo.get_by_id(fact_id)
    if fact is None or fact.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fact '{fact_id}' not found in workspace '{workspace_id}'",
        )

    return FactRead.model_validate(fact)
