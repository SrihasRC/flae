from datetime import datetime
from typing import Any, Optional
import uuid

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.fact import Fact
from app.models.workspace import Workspace


class Arbitration(Base):
    """SQLAlchemy ORM model for pairwise cross-document fact adjudication records."""

    __tablename__ = "arbitrations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    fact_a_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("facts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fact_b_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("facts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    divergence_factor: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )
    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    reasoning_trace: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    evidence_comparison: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    def __init__(self, **kwargs: Any) -> None:
        if "arbitration_id" in kwargs and "id" not in kwargs:
            kwargs["id"] = kwargs.pop("arbitration_id")
        kwargs.setdefault("id", uuid.uuid4())
        kwargs.setdefault("evidence_comparison", {})
        kwargs.setdefault("created_at", datetime.utcnow())
        super().__init__(**kwargs)

    @property
    def arbitration_id(self) -> uuid.UUID:
        """Alias for id property matching API and schema specifications."""
        return self.id

    @arbitration_id.setter
    def arbitration_id(self, value: uuid.UUID) -> None:
        self.id = value

    def __repr__(self) -> str:
        return f"<Arbitration(id={self.id}, relationship='{self.relationship}', confidence={self.confidence_score})>"
