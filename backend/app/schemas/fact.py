"""Pydantic v2 schemas for Atomic Facts, Context Envelopes, and Evidence."""

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

PeriodType = Literal["duration", "point_in_time"]
EntityScope = Literal["consolidated", "standalone", "subsidiary", "cohort"]
AccountingMethodology = Literal[
    "reported_ind_as",
    "pro_forma",
    "first_advance_estimate",
    "second_advance_estimate",
    "revised_estimate",
    "budget_estimate",
    "actual",
    "not_applicable",
]


class ContextEnvelope(BaseModel):
    """Context qualifiers surrounding an atomic fact measurement."""

    model_config = ConfigDict(from_attributes=True)

    temporal_period: Optional[str] = Field(
        default=None, description="Timeframe of the claim, e.g. 'FY2023-24' or 'Q3 FY24'"
    )
    period_type: Optional[str] = Field(
        default=None, description="'duration' for period spans or 'point_in_time' for snapshot dates"
    )
    entity_scope: Optional[str] = Field(
        default=None, description="Reporting perimeter, e.g. consolidated or standalone"
    )
    geography: Optional[str] = Field(
        default=None, description="Geographic jurisdiction or region, e.g. 'India'"
    )
    accounting_methodology: Optional[str] = Field(
        default=None, description="Accounting or statistical reporting methodology"
    )
    additional_qualifiers: Optional[str] = Field(
        default=None, description="Other qualifiers like currency denomination, audit status, etc."
    )

    @field_validator(
        "period_type", "entity_scope", "accounting_methodology", mode="before"
    )
    @classmethod
    def normalize_case(cls, v: Any) -> Any:
        if isinstance(v, str):
            cleaned = v.strip().lower()
            return cleaned if cleaned else None
        return v


class Evidence(BaseModel):
    """Grounding evidence and verbatim citation from the source document."""

    model_config = ConfigDict(from_attributes=True)

    verbatim_quote: str = Field(
        ..., description="Exact textual excerpt from the PDF grounding this fact"
    )
    page_number: int = Field(
        ..., ge=1, description="1-indexed physical page number of the citation"
    )
    section_title: Optional[str] = Field(
        default=None, description="Heading or chapter title containing the fact"
    )


class FactCreate(BaseModel):
    """Payload for creating an ungrounded or extracted atomic fact."""

    subject: str = Field(..., description="Entity or topic of the claim")
    attribute: str = Field(..., description="Property, metric, or relation measured")
    value_raw: str = Field(..., description="Raw text value as reported")
    value_numeric: Optional[float] = Field(
        default=None, description="Normalized numeric representation if applicable"
    )
    unit: Optional[str] = Field(
        default=None, description="Measurement unit, e.g. 'INR_Millions'"
    )
    context_envelope: ContextEnvelope = Field(
        default_factory=ContextEnvelope, description="Contextual qualification envelope"
    )
    evidence: Evidence = Field(
        ..., description="Verbatim quote and source page citation"
    )

    @field_validator("context_envelope", mode="before")
    @classmethod
    def ensure_envelope(cls, v: Any) -> Any:
        return {} if v is None else v


class FactRead(BaseModel):
    """Canonical Atomic Fact representation stored in the ledger."""

    model_config = ConfigDict(from_attributes=True)

    fact_id: uuid.UUID = Field(..., description="Unique fact UUID")
    document_id: uuid.UUID = Field(..., description="Source document UUID")
    workspace_id: uuid.UUID = Field(..., description="Parent workspace UUID")
    subject: str = Field(..., description="Entity or topic of the claim")
    attribute: str = Field(..., description="Property, metric, or relation measured")
    value_raw: str = Field(..., description="Raw text value as reported")
    value_numeric: Optional[float] = Field(
        default=None, description="Normalized numeric representation if applicable"
    )
    unit: Optional[str] = Field(
        default=None, description="Measurement unit, e.g. 'INR_Millions'"
    )
    context_envelope: ContextEnvelope = Field(
        default_factory=ContextEnvelope, description="Contextual qualification envelope"
    )
    evidence: Evidence = Field(
        ..., description="Verbatim quote and source page citation"
    )
    created_at: datetime = Field(..., description="Timestamp of ledger entry creation")

    @field_validator("context_envelope", mode="before")
    @classmethod
    def ensure_envelope(cls, v: Any) -> Any:
        return {} if v is None else v


class FactListResponse(BaseModel):
    """Paginated list of facts in a workspace."""

    model_config = ConfigDict(from_attributes=True)

    facts: list[FactRead] = Field(
        default_factory=list, description="List of atomic facts"
    )
    total: int = Field(default=0, ge=0, description="Total count of matching facts")
