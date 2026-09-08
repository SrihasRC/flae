"""Pydantic v2 schemas for Fact Arbitration, Evidence Comparison, and Case Explorer."""

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

ArbitrationRelationship = Literal[
    "CORROBORATED", "CONTRADICTED", "RECONCILED", "UNRELATED"
]


class EvidenceComparison(BaseModel):
    """Side-by-side evidence quotes and page citations compared by Arbiter."""

    model_config = ConfigDict(from_attributes=True)

    fact_a_quote: str = Field(
        ..., description="Verbatim quote from the first fact (Fact A)"
    )
    fact_a_page: int = Field(
        ..., ge=1, description="Page number where Fact A was cited"
    )
    fact_b_quote: str = Field(
        ..., description="Verbatim quote from the second fact (Fact B)"
    )
    fact_b_page: int = Field(
        ..., ge=1, description="Page number where Fact B was cited"
    )


class ArbitrationRead(BaseModel):
    """Full arbitration adjudication result for a pair of facts."""

    model_config = ConfigDict(from_attributes=True)

    arbitration_id: uuid.UUID = Field(
        ..., description="Unique arbitration adjudication UUID"
    )
    fact_a_id: uuid.UUID = Field(..., description="UUID of the first fact")
    fact_b_id: uuid.UUID = Field(..., description="UUID of the second fact")
    workspace_id: uuid.UUID = Field(..., description="Parent workspace UUID")
    relationship: ArbitrationRelationship = Field(
        ..., description="Adjudicated relationship: CORROBORATED, CONTRADICTED, RECONCILED, or UNRELATED"
    )
    divergence_factor: Optional[str] = Field(
        default=None,
        description="Key dimension explaining divergence (e.g. 'entity_scope: Standalone vs Consolidated')",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 assigned by Arbiter",
    )
    reasoning_trace: str = Field(
        ..., description="Detailed step-by-step reasoning trace explaining the verdict"
    )
    evidence_comparison: EvidenceComparison = Field(
        ..., description="Juxtaposed evidence quotes and citations"
    )
    created_at: datetime = Field(
        ..., description="Timestamp when arbitration was executed"
    )

    @field_validator("relationship", mode="before")
    @classmethod
    def normalize_relationship(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().upper()
        return v


class ArbitrationListResponse(BaseModel):
    """Paginated list response for arbitration results in a workspace."""

    model_config = ConfigDict(from_attributes=True)

    arbitrations: list[ArbitrationRead] = Field(
        default_factory=list, description="List of arbitration adjudication results"
    )
    total: int = Field(
        default=0, ge=0, description="Total count of matching arbitrations"
    )


class ArbitrationTriggerRequest(BaseModel):
    """Request payload to manually trigger arbitration for a workspace."""

    workspace_id: Optional[uuid.UUID] = Field(
        default=None, description="Target workspace UUID (optional if specified in path)"
    )
    force_rerun: bool = Field(
        default=False,
        description="If true, clears existing results and re-arbitrates all candidate pairs",
    )


class ArbitrationTriggerResponse(BaseModel):
    """Response payload returned when an arbitration job is accepted."""

    model_config = ConfigDict(from_attributes=True)

    job_id: str = Field(..., description="Unique identifier for the background job")
    workspace_id: uuid.UUID = Field(..., description="Target workspace UUID")
    status: str = Field(default="accepted", description="Status of the dispatched job")
    message: str = Field(
        ..., description="Human-readable description of the dispatched job"
    )


class CaseExplorerResponse(BaseModel):
    """Curated showcase partitions for Case 1 (Corroborated), Case 2 (Contradicted), and Case 3 (Reconciled)."""

    model_config = ConfigDict(from_attributes=True)

    case_1_corroborated: list[ArbitrationRead] = Field(
        default_factory=list, description="Corroborated fact pairs across documents"
    )
    case_2_contradicted: list[ArbitrationRead] = Field(
        default_factory=list, description="Contradicted fact pairs with genuine conflict"
    )
    case_3_reconciled: list[ArbitrationRead] = Field(
        default_factory=list, description="Reconciled fact pairs with divergence factors"
    )
