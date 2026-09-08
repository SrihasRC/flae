from typing import Any, Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace


class WorkspaceRepository:
    """Async repository for Workspace CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @staticmethod
    def _to_uuid(val: uuid.UUID | str) -> uuid.UUID:
        if isinstance(val, uuid.UUID):
            return val
        return uuid.UUID(str(val))

    async def create(self, data: dict[str, Any]) -> Workspace:
        """Create a new workspace."""
        payload = dict(data)
        if "id" in payload and payload["id"] is not None:
            payload["id"] = self._to_uuid(payload["id"])
        workspace = Workspace(**payload)
        self.db.add(workspace)
        await self.db.flush()
        await self.db.refresh(workspace)
        return workspace

    async def get_by_id(self, id: uuid.UUID | str) -> Optional[Workspace]:
        """Retrieve a workspace by primary key."""
        uid = self._to_uuid(id)
        stmt = select(Workspace).where(Workspace.id == uid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Workspace]:
        """Retrieve a workspace by unique name."""
        stmt = select(Workspace).where(Workspace.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Workspace]:
        """List all workspaces ordered by creation date descending."""
        stmt = select(Workspace).order_by(Workspace.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, id: uuid.UUID | str) -> bool:
        """Delete a workspace by primary key. Returns True if deleted, False if not found."""
        workspace = await self.get_by_id(id)
        if workspace is None:
            return False
        await self.db.delete(workspace)
        await self.db.flush()
        return True
