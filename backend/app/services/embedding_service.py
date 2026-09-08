import asyncio
import inspect
import logging
from typing import Any, Optional, Union

from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)


def _extract_embedding_values(embedding_item: Any) -> list[float]:
    """Extract float values from a single embedding item returned by the SDK or mock."""
    if hasattr(embedding_item, "values") and embedding_item.values is not None:
        return [float(x) for x in embedding_item.values]
    if isinstance(embedding_item, (list, tuple)):
        return [float(x) for x in embedding_item]
    if isinstance(embedding_item, dict) and "values" in embedding_item:
        return [float(x) for x in embedding_item["values"]]
    raise ValueError(f"Unable to extract embedding values from {embedding_item}")


class EmbeddingService:
    """Service for computing semantic embeddings using Google Gemini embedding models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        client: Optional[genai.Client] = None,
    ) -> None:
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or "gemini-embedding-2"
        if client is not None:
            self.client = client
        else:
            api_key_to_use = self.api_key if self.api_key else "placeholder_api_key"
            self.client = genai.Client(api_key=api_key_to_use)

    async def _call_embed_content(
        self,
        contents: Union[str, list[str]],
    ) -> Any:
        """Invoke client.models.embed_content asynchronously without blocking the event loop."""
        embed_fn = self.client.models.embed_content
        if inspect.iscoroutinefunction(embed_fn):
            return await embed_fn(model=self.model, contents=contents)
        res = await asyncio.to_thread(embed_fn, model=self.model, contents=contents)
        if inspect.isawaitable(res):
            return await res
        return res

    async def embed_fact_anchor(self, subject: str, attribute: str) -> list[float]:
        """Embed a single fact anchor representation formatted as '{subject} | {attribute}'.

        Args:
            subject: The entity or subject of the atomic fact.
            attribute: The attribute or metric associated with the subject.

        Returns:
            A list of float values representing the embedding vector.
        """
        anchor = f"{subject} | {attribute}"
        try:
            response = await self._call_embed_content(contents=anchor)
            raw_embeddings = getattr(response, "embeddings", None)
            if raw_embeddings is None and isinstance(response, dict):
                raw_embeddings = response.get("embeddings")

            if raw_embeddings:
                return _extract_embedding_values(raw_embeddings[0])

            if hasattr(response, "embedding") and response.embedding is not None:
                return _extract_embedding_values(response.embedding)

            raise ValueError(f"No embeddings found in response: {response}")
        except Exception as exc:
            logger.exception("Failed to embed fact anchor '%s': %s", anchor, exc)
            raise

    async def embed_batch(self, anchors: list[str]) -> list[list[float]]:
        """Compute embeddings for a list of anchor strings in batches of up to 100.

        Args:
            anchors: List of anchor strings to embed.

        Returns:
            A list of float vectors corresponding to the input anchors.
        """
        if not anchors:
            return []

        batch_size = 100
        all_embeddings: list[list[float]] = []

        try:
            for i in range(0, len(anchors), batch_size):
                batch = anchors[i : i + batch_size]
                response = await self._call_embed_content(contents=batch)

                raw_embeddings = getattr(response, "embeddings", None)
                if raw_embeddings is None and isinstance(response, dict):
                    raw_embeddings = response.get("embeddings")

                if not raw_embeddings:
                    raise ValueError(
                        f"No embeddings returned for batch index {i // batch_size}."
                    )

                batch_vectors = [
                    _extract_embedding_values(item) for item in raw_embeddings
                ]
                all_embeddings.extend(batch_vectors)

            logger.info("Embedding batch complete (%d facts)", len(anchors))
            return all_embeddings
        except Exception as exc:
            logger.exception("Failed to embed batch of %d anchors: %s", len(anchors), exc)
            raise
