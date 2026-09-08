from datetime import datetime
from typing import Any, Optional
import uuid

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Fact(Base):
    """SQLAlchemy ORM model for atomic extracted facts with context envelopes."""

    __tablename__ = "facts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    attribute: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    value_raw: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    value_numeric: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        default=None,
    )
    unit: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )
    context_envelope: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    evidence: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    embedding_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    def __init__(self, **kwargs: Any) -> None:
        if "fact_id" in kwargs and "id" not in kwargs:
            kwargs["id"] = kwargs.pop("fact_id")
        kwargs.setdefault("id", uuid.uuid4())
        kwargs.setdefault("context_envelope", {})
        kwargs.setdefault("evidence", {})
        kwargs.setdefault("created_at", datetime.utcnow())
        super().__init__(**kwargs)

    @property
    def fact_id(self) -> uuid.UUID:
        """Alias for id property matching API and schema specifications."""
        return self.id

    @fact_id.setter
    def fact_id(self, value: uuid.UUID) -> None:
        self.id = value

    def __repr__(self) -> str:
        return f"<Fact(id={self.id}, subject='{self.subject}', attribute='{self.attribute}', value='{self.value_raw}')>"
