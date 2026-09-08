from typing import Any, Optional
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentRepository:
    """Async repository for Document CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @staticmethod
    def _to_uuid(val: uuid.UUID | str) -> uuid.UUID:
        if isinstance(val, uuid.UUID):
            return val
        return uuid.UUID(str(val))

    async def create(self, data: dict[str, Any]) -> Document:
        """Create a new document record."""
        payload = dict(data)
        if "id" in payload and payload["id"] is not None:
            payload["id"] = self._to_uuid(payload["id"])
        if "workspace_id" in payload and payload["workspace_id"] is not None:
            payload["workspace_id"] = self._to_uuid(payload["workspace_id"])
        doc = Document(**payload)
        self.db.add(doc)
        await self.db.flush()
        await self.db.refresh(doc)
        return doc

    async def get_by_id(self, id: uuid.UUID | str) -> Optional[Document]:
        """Retrieve a document by primary key."""
        uid = self._to_uuid(id)
        stmt = select(Document).where(Document.id == uid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_workspace(self, workspace_id: uuid.UUID | str) -> list[Document]:
        """List all documents for a given workspace ordered by upload date descending."""
        ws_uid = self._to_uuid(workspace_id)
        stmt = (
            select(Document)
            .where(Document.workspace_id == ws_uid)
            .order_by(Document.uploaded_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        doc_id: uuid.UUID | str,
        status: str,
        facts_extracted: Optional[int] = None,
        error: Optional[str] = None,
    ) -> Optional[Document]:
        """Update ingestion status, facts count, and error description for a document."""
        doc = await self.get_by_id(doc_id)
        if doc is None:
            return None
        doc.status = status
        if facts_extracted is not None:
            doc.facts_extracted = facts_extracted
        if error is not None:
            doc.error = error
        await self.db.flush()
        await self.db.refresh(doc)
        return doc

    async def count_by_workspace(self, workspace_id: uuid.UUID | str) -> int:
        """Return total number of documents in a workspace."""
        ws_uid = self._to_uuid(workspace_id)
        stmt = select(func.count(Document.id)).where(Document.workspace_id == ws_uid)
        result = await self.db.execute(stmt)
        count = result.scalar_one()
        return int(count or 0)

    async def delete(self, id: uuid.UUID | str) -> bool:
        """Delete a document by primary key. Returns True if deleted, False if not found."""
        doc = await self.get_by_id(id)
        if doc is None:
            return False
        await self.db.delete(doc)
        await self.db.flush()
        return True
