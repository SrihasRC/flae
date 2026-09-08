import logging
import uuid
from typing import Any, Optional, Union

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection

from app.core.config import settings

logger = logging.getLogger(__name__)


def _sanitize_metadata(metadata: dict[str, Any]) -> dict[str, Union[str, int, float, bool]]:
    """Sanitize metadata values so ChromaDB accepts them (e.g., converting UUIDs to strings)."""
    clean: dict[str, Union[str, int, float, bool]] = {}
    for key, value in metadata.items():
        if isinstance(value, uuid.UUID):
            clean[key] = str(value)
        elif isinstance(value, (str, int, float, bool)):
            clean[key] = value
        elif value is None:
            continue
        else:
            clean[key] = str(value)
    return clean


class VectorStoreService:
    """Service for managing workspace-partitioned ChromaDB vector indices for semantic blocking."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        persistent_path: Optional[str] = None,
        client: Optional[ClientAPI] = None,
    ) -> None:
        self._host = host or settings.CHROMA_HOST
        self._port = port or settings.CHROMA_PORT
        self._persistent_path = persistent_path or settings.CHROMA_PERSISTENT_PATH
        self._client: Optional[ClientAPI] = client
        if self._client is None:
            try:
                self._client = self._init_client()
            except Exception as exc:
                logger.warning(
                    "Could not initialize Chroma client during service startup (%s). "
                    "Client connection will be deferred until first operation.",
                    exc,
                )

    def _init_client(self) -> ClientAPI:
        """Initialize ChromaDB client.

        Tries connecting via HttpClient first. If CHROMA_HOST is 'localhost' and no external
        Chroma HTTP server responds, or if HttpClient fails, seamlessly falls back to
        chromadb.PersistentClient(path=settings.CHROMA_PERSISTENT_PATH).
        """
        try:
            client = chromadb.HttpClient(host=self._host, port=self._port)
            client.heartbeat()
            logger.info("ChromaDB connected at %s:%s", self._host, self._port)
            return client
        except Exception as exc:
            logger.info(
                "Could not connect to Chroma HTTP server at %s:%s (%s). "
                "Falling back to PersistentClient at %s.",
                self._host,
                self._port,
                exc,
                self._persistent_path,
            )
            try:
                client = chromadb.PersistentClient(path=self._persistent_path)
                client.heartbeat()
                logger.info(
                    "ChromaDB ready (PersistentClient at %s)", self._persistent_path
                )
                return client
            except Exception as persist_exc:
                logger.error(
                    "Failed to initialize PersistentClient at %s: %s",
                    self._persistent_path,
                    persist_exc,
                )
                raise

    @property
    def client(self) -> ClientAPI:
        """Get or initialize the ChromaDB client lazily."""
        if self._client is None:
            self._client = self._init_client()
        return self._client

    @client.setter
    def client(self, value: ClientAPI) -> None:
        """Allow setting or overriding the ChromaDB client (e.g. for testing)."""
        self._client = value

    @property
    def client_type(self) -> str:
        """Return 'persistent' or 'http' based on active Chroma client configuration."""
        try:
            settings_obj = self.client.get_settings()
            if getattr(settings_obj, "is_persistent", False):
                return "persistent"
        except Exception:
            pass
        return "http"

    def get_or_create_collection(self, workspace_id: Union[str, uuid.UUID]) -> Collection:
        """Retrieve or create an isolated collection for a specific workspace.

        Args:
            workspace_id: UUID or string identifier of the workspace.

        Returns:
            ChromaDB Collection partitioned for the workspace with cosine distance metric.
        """
        name = f"{settings.CHROMA_COLLECTION_PREFIX}_{str(workspace_id).replace('-', '_')}"
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_fact(
        self,
        workspace_id: Union[str, uuid.UUID],
        fact_id: Union[str, uuid.UUID],
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Upsert a fact embedding and its associated metadata into the workspace collection.

        Args:
            workspace_id: UUID or string identifier of the workspace.
            fact_id: UUID or string unique identifier of the fact.
            embedding: Dense vector representation of the fact anchor.
            metadata: Associated metadata dictionary (e.g. document_id, subject, attribute).
        """
        collection = self.get_or_create_collection(workspace_id)
        clean_metadata = _sanitize_metadata(metadata)
        collection.upsert(
            ids=[str(fact_id)],
            embeddings=[embedding],
            metadatas=[clean_metadata],
        )

    def query_candidates(
        self,
        workspace_id: Union[str, uuid.UUID, list[float]],
        embedding: Union[list[float], str, uuid.UUID],
        exclude_document_id: Union[str, uuid.UUID],
        top_k: int = 20,
        threshold: float = 0.82,
    ) -> list[dict[str, Any]]:
        """Query top candidate facts for cross-document arbitration based on cosine similarity.

        Args:
            workspace_id: UUID or string workspace ID (or embedding if arguments are swapped).
            embedding: Query embedding vector (or workspace ID if arguments are swapped).
            exclude_document_id: Document ID to exclude from candidate matching (prevents self-matching).
            top_k: Maximum number of candidates to retrieve.
            threshold: Minimum cosine similarity score required (default: 0.82).

        Returns:
            List of candidate dictionaries: [{"fact_id": str, "score": float, "metadata": dict}]
        """
        # Handle swapped arguments in case caller passes (embedding, workspace_id, ...)
        if isinstance(workspace_id, (list, tuple)) and (
            isinstance(embedding, (str, uuid.UUID)) or embedding is None
        ):
            workspace_id, embedding = embedding, workspace_id

        collection = self.get_or_create_collection(workspace_id)
        total_count = collection.count()
        if total_count == 0:
            return []

        n_results = min(top_k, max(1, total_count))
        results = collection.query(
            query_embeddings=[embedding],  # type: ignore[list-item]
            n_results=n_results,
        )

        candidates: list[dict[str, Any]] = []
        if not results or not results.get("ids") or not results["ids"][0]:
            return candidates

        exclude_doc_str = (
            str(exclude_document_id) if exclude_document_id is not None else ""
        )

        for i, doc_id in enumerate(results["ids"][0]):
            meta = (
                results["metadatas"][0][i]
                if results.get("metadatas") and len(results["metadatas"][0]) > i
                else {}
            )
            distance = (
                results["distances"][0][i]
                if results.get("distances") and len(results["distances"][0]) > i
                else 0.0
            )
            score = 1.0 - float(distance)  # cosine metric: distance = 1 - similarity

            candidate_doc_id = str(meta.get("document_id", "")) if meta else ""
            if candidate_doc_id != exclude_doc_str and score >= threshold:
                candidates.append({
                    "fact_id": doc_id,
                    "score": score,
                    "metadata": meta,
                })

        return candidates

    def delete_by_document(
        self,
        workspace_id: Union[str, uuid.UUID],
        document_id: Union[str, uuid.UUID],
    ) -> None:
        """Delete all indexed facts belonging to a specific document.

        Args:
            workspace_id: UUID or string identifier of the workspace.
            document_id: UUID or string identifier of the document to purge.
        """
        collection = self.get_or_create_collection(workspace_id)
        results = collection.get(where={"document_id": str(document_id)})
        if results and results.get("ids"):
            collection.delete(ids=results["ids"])

    def delete_collection(self, workspace_id: Union[str, uuid.UUID]) -> None:
        """Delete an entire workspace collection from the vector store.

        Args:
            workspace_id: UUID or string identifier of the workspace.
        """
        name = f"{settings.CHROMA_COLLECTION_PREFIX}_{str(workspace_id).replace('-', '_')}"
        try:
            self.client.delete_collection(name)
        except Exception as exc:
            logger.debug(
                "Failed to delete collection '%s' or collection did not exist: %s",
                name,
                exc,
            )
