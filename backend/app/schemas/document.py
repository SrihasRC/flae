"""Pydantic v2 schemas for Document domain models and ingestion statuses."""

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

DocumentStatus = Literal["pending", "processing", "complete", "failed"]


class DocumentRead(BaseModel):
    """Full document metadata representation."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique document UUID")
    filename: str = Field(..., description="Original name of the uploaded PDF")
    workspace_id: uuid.UUID = Field(..., description="Parent workspace UUID")
    page_count: int = Field(
        default=0, ge=0, description="Total page count of the PDF"
    )
    status: DocumentStatus = Field(
        default="pending", description="Current pipeline processing status"
    )
    uploaded_at: datetime = Field(..., description="Timestamp when document was uploaded")

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class DocumentListResponse(BaseModel):
    """Response payload for listing documents in a workspace."""

    model_config = ConfigDict(from_attributes=True)

    documents: list[DocumentRead] = Field(
        default_factory=list, description="List of documents in the workspace"
    )


class IngestionJobStatus(BaseModel):
    """Status polling response for asynchronous PDF ingestion pipeline."""

    model_config = ConfigDict(from_attributes=True)

    document_id: uuid.UUID = Field(..., description="Target document UUID")
    status: str = Field(..., description="Pipeline execution stage or status")
    facts_extracted: int = Field(
        default=0, ge=0, description="Number of atomic facts extracted so far"
    )
    error: Optional[str] = Field(
        default=None, description="Error message if pipeline execution failed"
    )


class DocumentUploadResponse(BaseModel):
    """Response payload returned when a document is accepted for ingestion."""

    model_config = ConfigDict(from_attributes=True)

    document_id: uuid.UUID = Field(..., description="Target document UUID")
    filename: str = Field(..., description="Original name of the uploaded PDF")
    workspace_id: uuid.UUID = Field(..., description="Parent workspace UUID")
    status: DocumentStatus = Field(
        default="pending", description="Initial pipeline status (typically pending)"
    )
    uploaded_at: datetime = Field(..., description="Timestamp of document upload")

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v
