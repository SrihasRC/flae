from typing import Any, Optional
import uuid

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fact import Fact


class FactRepository:
    """Async repository for Fact CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @staticmethod
    def _to_uuid(val: uuid.UUID | str) -> uuid.UUID:
        if isinstance(val, uuid.UUID):
            return val
        return uuid.UUID(str(val))

    async def create(self, data: dict[str, Any]) -> Fact:
        """Create a single fact record."""
        created = await self.create_bulk([data])
        return created[0]

    async def create_bulk(self, facts: list[dict[str, Any]]) -> list[Fact]:
        """Bulk insert extracted facts into the database."""
        if not facts:
            return []

        fact_objs: list[Fact] = []
        for item in facts:
            payload = dict(item)
            fact_id = payload.pop("fact_id", None)
            if "id" not in payload and fact_id is not None:
                payload["id"] = fact_id
            if "id" in payload and payload["id"] is not None:
                payload["id"] = self._to_uuid(payload["id"])
            if "document_id" in payload and payload["document_id"] is not None:
                payload["document_id"] = self._to_uuid(payload["document_id"])
            if "workspace_id" in payload and payload["workspace_id"] is not None:
                payload["workspace_id"] = self._to_uuid(payload["workspace_id"])

            envelope = payload.get("context_envelope")
            if hasattr(envelope, "model_dump"):
                payload["context_envelope"] = envelope.model_dump()
            elif envelope is None:
                payload["context_envelope"] = {}

            evidence = payload.get("evidence")
            if hasattr(evidence, "model_dump"):
                payload["evidence"] = evidence.model_dump()
            elif evidence is None:
                payload["evidence"] = {}

            fact_objs.append(Fact(**payload))

        self.db.add_all(fact_objs)
        await self.db.flush()
        for obj in fact_objs:
            await self.db.refresh(obj)
        return fact_objs

    async def get_by_id(self, id: uuid.UUID | str) -> Optional[Fact]:
        """Retrieve a fact by primary key."""
        uid = self._to_uuid(id)
        stmt = select(Fact).where(Fact.id == uid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_workspace(
        self,
        workspace_id: uuid.UUID | str,
        skip: int = 0,
        limit: int = 50,
        document_id: Optional[uuid.UUID | str] = None,
        subject: Optional[str] = None,
        attribute: Optional[str] = None,
        query: Optional[str] = None,
    ) -> list[Fact]:
        """List facts for a workspace with pagination and optional filters."""
        ws_uid = self._to_uuid(workspace_id)
        stmt = select(Fact).where(Fact.workspace_id == ws_uid)

        if document_id is not None:
            stmt = stmt.where(Fact.document_id == self._to_uuid(document_id))
        if subject:
            stmt = stmt.where(Fact.subject.ilike(f"%{subject}%"))
        if attribute:
            stmt = stmt.where(Fact.attribute.ilike(f"%{attribute}%"))
        if query and query.strip():
            terms = [t.strip() for t in query.split(",") if t.strip()]
            if terms:
                term_conditions = []
                for term in terms:
                    q_term = f"%{term}%"
                    term_conditions.extend([
                        Fact.subject.ilike(q_term),
                        Fact.attribute.ilike(q_term),
                        Fact.value_raw.ilike(q_term),
                    ])
                stmt = stmt.where(or_(*term_conditions))

        stmt = stmt.offset(skip).limit(limit).order_by(Fact.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_by_document(self, doc_id: uuid.UUID | str) -> list[Fact]:
        """List all facts extracted from a specific document."""
        doc_uid = self._to_uuid(doc_id)
        stmt = select(Fact).where(Fact.document_id == doc_uid).order_by(Fact.created_at.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_workspace(
        self,
        workspace_id: uuid.UUID | str,
        document_id: Optional[uuid.UUID | str] = None,
        subject: Optional[str] = None,
        attribute: Optional[str] = None,
        query: Optional[str] = None,
    ) -> int:
        """Return total number of facts in a workspace matching optional filters."""
        ws_uid = self._to_uuid(workspace_id)
        stmt = select(func.count(Fact.id)).where(Fact.workspace_id == ws_uid)

        if document_id is not None:
            stmt = stmt.where(Fact.document_id == self._to_uuid(document_id))
        if subject:
            stmt = stmt.where(Fact.subject.ilike(f"%{subject}%"))
        if attribute:
            stmt = stmt.where(Fact.attribute.ilike(f"%{attribute}%"))
        if query and query.strip():
            terms = [t.strip() for t in query.split(",") if t.strip()]
            if terms:
                term_conditions = []
                for term in terms:
                    q_term = f"%{term}%"
                    term_conditions.extend([
                        Fact.subject.ilike(q_term),
                        Fact.attribute.ilike(q_term),
                        Fact.value_raw.ilike(q_term),
                    ])
                stmt = stmt.where(or_(*term_conditions))

        result = await self.db.execute(stmt)
        count = result.scalar_one()
        return int(count or 0)

    async def delete_by_document(self, doc_id: uuid.UUID | str) -> int:
        """Delete all facts belonging to a document. Returns number of rows deleted."""
        doc_uid = self._to_uuid(doc_id)
        stmt = delete(Fact).where(Fact.document_id == doc_uid)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return int(result.rowcount or 0)

    async def delete(self, id: uuid.UUID | str) -> bool:
        """Delete a fact by primary key. Returns True if deleted, False if not found."""
        fact = await self.get_by_id(id)
        if fact is None:
            return False
        await self.db.delete(fact)
        await self.db.flush()
        return True
