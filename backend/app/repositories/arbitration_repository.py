from typing import Any, Optional
import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.arbitration import Arbitration


class ArbitrationRepository:
    """Async repository for Arbitration CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @staticmethod
    def _to_uuid(val: uuid.UUID | str) -> uuid.UUID:
        if isinstance(val, uuid.UUID):
            return val
        return uuid.UUID(str(val))

    async def create(self, data: dict[str, Any]) -> Arbitration:
        """Create a single arbitration record."""
        created = await self.create_bulk([data])
        return created[0]

    async def create_bulk(self, arbs: list[dict[str, Any]]) -> list[Arbitration]:
        """Bulk insert arbitration records into the database."""
        if not arbs:
            return []

        arb_objs: list[Arbitration] = []
        for item in arbs:
            payload = dict(item)
            arb_id = payload.pop("arbitration_id", None)
            if "id" not in payload and arb_id is not None:
                payload["id"] = arb_id
            if "id" in payload and payload["id"] is not None:
                payload["id"] = self._to_uuid(payload["id"])
            if "fact_a_id" in payload and payload["fact_a_id"] is not None:
                payload["fact_a_id"] = self._to_uuid(payload["fact_a_id"])
            if "fact_b_id" in payload and payload["fact_b_id"] is not None:
                payload["fact_b_id"] = self._to_uuid(payload["fact_b_id"])
            if "workspace_id" in payload and payload["workspace_id"] is not None:
                payload["workspace_id"] = self._to_uuid(payload["workspace_id"])

            comparison = payload.get("evidence_comparison")
            if hasattr(comparison, "model_dump"):
                payload["evidence_comparison"] = comparison.model_dump()
            elif comparison is None:
                payload["evidence_comparison"] = {}

            arb_objs.append(Arbitration(**payload))

        self.db.add_all(arb_objs)
        await self.db.flush()
        for obj in arb_objs:
            await self.db.refresh(obj)
        return arb_objs

    async def get_by_id(self, id: uuid.UUID | str) -> Optional[Arbitration]:
        """Retrieve an arbitration record by primary key."""
        uid = self._to_uuid(id)
        stmt = select(Arbitration).where(Arbitration.id == uid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_workspace(
        self,
        workspace_id: uuid.UUID | str,
        skip: int = 0,
        limit: int = 50,
        relationship_filter: Optional[str] = None,
        min_confidence: Optional[float] = None,
    ) -> list[Arbitration]:
        """List arbitrations for a workspace with pagination and optional filters."""
        ws_uid = self._to_uuid(workspace_id)
        stmt = select(Arbitration).where(Arbitration.workspace_id == ws_uid)

        if relationship_filter:
            stmt = stmt.where(Arbitration.relationship == relationship_filter)
        if min_confidence is not None:
            stmt = stmt.where(Arbitration.confidence_score >= min_confidence)

        stmt = stmt.offset(skip).limit(limit).order_by(Arbitration.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_by_relationship(
        self,
        workspace_id: uuid.UUID | str,
        relationship: str,
    ) -> list[Arbitration]:
        """List arbitrations for a workspace filtered by specific relationship class."""
        ws_uid = self._to_uuid(workspace_id)
        stmt = (
            select(Arbitration)
            .where(
                Arbitration.workspace_id == ws_uid,
                Arbitration.relationship == relationship,
            )
            .order_by(Arbitration.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_workspace(
        self,
        workspace_id: uuid.UUID | str,
        relationship_filter: Optional[str] = None,
        min_confidence: Optional[float] = None,
    ) -> int:
        """Return total count of arbitrations matching criteria in a workspace."""
        ws_uid = self._to_uuid(workspace_id)
        stmt = select(func.count(Arbitration.id)).where(Arbitration.workspace_id == ws_uid)

        if relationship_filter:
            stmt = stmt.where(Arbitration.relationship == relationship_filter)
        if min_confidence is not None:
            stmt = stmt.where(Arbitration.confidence_score >= min_confidence)

        result = await self.db.execute(stmt)
        count = result.scalar_one()
        return int(count or 0)

    async def delete_by_workspace(self, workspace_id: uuid.UUID | str) -> int:
        """Delete all arbitration records in a workspace. Returns number of rows deleted."""
        ws_uid = self._to_uuid(workspace_id)
        stmt = delete(Arbitration).where(Arbitration.workspace_id == ws_uid)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return int(result.rowcount or 0)

    async def delete(self, id: uuid.UUID | str) -> bool:
        """Delete an arbitration record by primary key. Returns True if deleted, False if not found."""
        arb = await self.get_by_id(id)
        if arb is None:
            return False
        await self.db.delete(arb)
        await self.db.flush()
        return True
