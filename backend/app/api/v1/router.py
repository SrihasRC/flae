"""Central API v1 router consolidating all sub-routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import arbitration, documents, facts, workspaces

api_router = APIRouter()

api_router.include_router(workspaces.router, prefix="/workspaces")
api_router.include_router(documents.router, prefix="/workspaces")
api_router.include_router(facts.router, prefix="/workspaces")
api_router.include_router(arbitration.router, prefix="/workspaces")
