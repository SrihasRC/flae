"""FastAPI router endpoints for arbitration trigger, list, cases, and detail."""

import logging
from typing import Optional
import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.core.database import AsyncSessionLocal
from app.dependencies import (
    get_arbitration_repo,
    get_workspace_repo,
)
from app.repositories.arbitration_repository import ArbitrationRepository
from app.repositories.fact_repository import FactRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.arbitration import (
    ArbitrationListResponse,
    ArbitrationRead,
    ArbitrationTriggerRequest,
    ArbitrationTriggerResponse,
    CaseExplorerResponse,
)
from app.services.arbitration_service import ArbitrationService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Arbitration"])


async def run_manual_arbitration(workspace_id: uuid.UUID) -> None:
    """Asynchronous background task for manual full-workspace fact arbitration.

    Creates its own async DB session to remain active after the HTTP request terminates.
    """
    try:
        async with AsyncSessionLocal() as session:
            local_fact_repo = FactRepository(session)
            local_arb_repo = ArbitrationRepository(session)
            local_emb_svc = EmbeddingService()
            local_vec_store = VectorStoreService()
            local_arb_svc = ArbitrationService(
                local_emb_svc, local_vec_store, local_fact_repo
            )

            results = await local_arb_svc.run_arbitration_for_workspace(workspace_id)
            if results:
                await local_arb_repo.create_bulk(
                    [
                        dict(result) | {"workspace_id": str(workspace_id)}
                        for result in results
                    ]
                )
            await session.commit()
            logger.info(
                "Manual arbitration complete for workspace %s: %d arbitrations",
                workspace_id,
                len(results),
            )
    except Exception as e:
        logger.error(
            "Manual arbitration failed for workspace %s: %s",
            workspace_id,
            e,
            exc_info=True,
        )


@router.post(
    "/{workspace_id}/arbitration/run",
    response_model=ArbitrationTriggerResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Manually trigger arbitration for a workspace",
)
async def trigger_arbitration(
    workspace_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    payload: Optional[ArbitrationTriggerRequest] = Body(default=None),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    arb_repo: ArbitrationRepository = Depends(get_arbitration_repo),
) -> ArbitrationTriggerResponse:
    """Manually trigger arbitration for an entire workspace with optional force rerun."""
    ws = await workspace_repo.get_by_id(workspace_id)
    if ws is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )

    force_rerun = payload.force_rerun if payload else False
    if force_rerun:
        await arb_repo.delete_by_workspace(workspace_id)

    background_tasks.add_task(run_manual_arbitration, workspace_id=workspace_id)

    job_id = f"arb-job-{str(workspace_id)[:8]}"
    return ArbitrationTriggerResponse(
        job_id=job_id,
        workspace_id=workspace_id,
        status="accepted",
        message=f"Arbitration job dispatched for workspace {ws.name}",
    )


@router.get(
    "/{workspace_id}/arbitration/cases",
    response_model=CaseExplorerResponse,
    status_code=status.HTTP_200_OK,
    summary="Case 1-4 Explorer for curated arbitration showcase",
)
async def get_arbitration_cases(
    workspace_id: uuid.UUID,
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    arb_repo: ArbitrationRepository = Depends(get_arbitration_repo),
) -> CaseExplorerResponse:
    """Case 1-4 Explorer returning curated sets of arbitration results (Corroborated, Contradicted, Reconciled).

    Defined before the parameterized arbitration_id route to prevent routing collisions.
    """
    ws = await workspace_repo.get_by_id(workspace_id)
    if ws is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )

    case_1 = await arb_repo.list_by_relationship(workspace_id, "CORROBORATED")
    case_2 = await arb_repo.list_by_relationship(workspace_id, "CONTRADICTED")
    case_3 = await arb_repo.list_by_relationship(workspace_id, "RECONCILED")

    return CaseExplorerResponse(
        case_1_corroborated=[ArbitrationRead.model_validate(a) for a in case_1],
        case_2_contradicted=[ArbitrationRead.model_validate(a) for a in case_2],
        case_3_reconciled=[ArbitrationRead.model_validate(a) for a in case_3],
    )


@router.get(
    "/{workspace_id}/arbitration",
    response_model=ArbitrationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all arbitration results for a workspace",
)
async def list_arbitrations(
    workspace_id: uuid.UUID,
    relationship: Optional[str] = Query(
        default=None,
        description="Filter by CORROBORATED, CONTRADICTED, RECONCILED, or UNRELATED",
    ),
    min_confidence: Optional[float] = Query(
        default=None,
        ge=0.0,
        le=1.0,
        description="Filter results with confidence_score >= value",
    ),
    skip: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=50, ge=1, le=200, description="Max results per page"),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    arb_repo: ArbitrationRepository = Depends(get_arbitration_repo),
) -> ArbitrationListResponse:
    """Retrieve paginated arbitration results for a workspace with optional filters."""
    ws = await workspace_repo.get_by_id(workspace_id)
    if ws is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )

    arbs = await arb_repo.list_by_workspace(
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
        relationship_filter=relationship,
        min_confidence=min_confidence,
    )
    total = await arb_repo.count_by_workspace(
        workspace_id=workspace_id,
        relationship_filter=relationship,
        min_confidence=min_confidence,
    )

    return ArbitrationListResponse(
        arbitrations=[ArbitrationRead.model_validate(a) for a in arbs],
        total=total,
    )


@router.get(
    "/{workspace_id}/arbitration/{arbitration_id}",
    response_model=ArbitrationRead,
    status_code=status.HTTP_200_OK,
    summary="Get single arbitration result by ID",
)
async def get_arbitration(
    workspace_id: uuid.UUID,
    arbitration_id: uuid.UUID,
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    arb_repo: ArbitrationRepository = Depends(get_arbitration_repo),
) -> ArbitrationRead:
    """Retrieve a single arbitration adjudication result by its UUID."""
    ws = await workspace_repo.get_by_id(workspace_id)
    if ws is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found",
        )

    arb = await arb_repo.get_by_id(arbitration_id)
    if arb is None or arb.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Arbitration '{arbitration_id}' not found in workspace '{workspace_id}'",
        )

    return ArbitrationRead.model_validate(arb)
