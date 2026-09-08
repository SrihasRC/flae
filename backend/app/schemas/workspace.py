"""Pydantic v2 schemas for Workspace domain models."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreate(BaseModel):
    """Payload for creating a new workspace partition."""

    name: str = Field(..., max_length=100, description="Unique workspace identifier")
    description: Optional[str] = Field(
        None, max_length=500, description="Optional workspace description"
    )


class WorkspaceRead(WorkspaceCreate):
    """Full workspace representation with system metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique workspace UUID")
    created_at: datetime = Field(..., description="Timestamp of workspace creation")
    document_count: int = Field(
        default=0, ge=0, description="Count of documents ingested in this workspace"
    )
    fact_count: int = Field(
        default=0, ge=0, description="Count of atomic facts extracted in this workspace"
    )


class WorkspaceListResponse(BaseModel):
    """Response payload for listing all workspaces."""

    model_config = ConfigDict(from_attributes=True)

    workspaces: list[WorkspaceRead] = Field(
        default_factory=list, description="List of workspaces"
    )
