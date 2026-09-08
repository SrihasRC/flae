"""
Embedding service using fastembed (ONNX-based, CPU-only, no PyTorch).
Falls back to Gemini embedding API if EMBEDDING_PROVIDER=gemini in env.
"""
import logging
import os
from typing import Generator

from fastembed import TextEmbedding
from app.core.config import settings

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
_BATCH_SIZE = 100


class EmbeddingService:
    """Lightweight ONNX-based embedding service via fastembed.

    Uses BAAI/bge-small-en-v1.5 by default (~90MB ONNX, no PyTorch).
    Falls back to Gemini embedding API when EMBEDDING_PROVIDER=gemini.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        provider: str | None = None,
    ):
        self._provider = (provider or os.getenv("EMBEDDING_PROVIDER", "fastembed")).lower()
        if self._provider == "fastembed":
            model_name = model or os.getenv("FASTEMBED_MODEL", _DEFAULT_MODEL)
            logger.info(f"Initializing fastembed model: {model_name}")
            self._model = TextEmbedding(model_name=model_name)
            logger.info("fastembed model loaded (ONNX CPU inference)")
        else:
            from google import genai
            gemini_key = api_key or settings.GEMINI_API_KEY or "placeholder_key"
            self._gemini_client = genai.Client(api_key=gemini_key)
            self._gemini_model = model or "gemini-embedding-2"
            logger.info("Using Gemini embedding API")

    def _build_anchor(self, subject: str, attribute: str) -> str:
        return f"{subject} | {attribute}"

    async def embed_fact_anchor(self, subject: str, attribute: str) -> list[float]:
        anchor = self._build_anchor(subject, attribute)
        results = await self.embed_batch([anchor])
        return results[0]

    async def embed_batch(self, anchors: list[str]) -> list[list[float]]:
        if not anchors:
            return []
        if self._provider == "fastembed":
            return self._embed_fastembed(anchors)
        else:
            return await self._embed_gemini(anchors)

    def _embed_fastembed(self, anchors: list[str]) -> list[list[float]]:
        """Synchronous fastembed inference (ONNX runs in process, no async needed)."""
        results = []
        # Process in batches
        for i in range(0, len(anchors), _BATCH_SIZE):
            batch = anchors[i : i + _BATCH_SIZE]
            embeddings: Generator = self._model.embed(batch)
            for emb in embeddings:
                results.append(emb.tolist())
        logger.info(f"Embedding batch complete ({len(results)} facts) via fastembed")
        return results

    async def _embed_gemini(self, anchors: list[str]) -> list[list[float]]:
        """Gemini embedding API fallback."""
        results = []
        for i in range(0, len(anchors), _BATCH_SIZE):
            batch = anchors[i : i + _BATCH_SIZE]
            for anchor in batch:
                response = self._gemini_client.models.embed_content(
                    model=self._gemini_model, contents=anchor
                )
                if hasattr(response, "embeddings") and response.embeddings:
                    results.append(list(response.embeddings[0].values))
                elif hasattr(response, "embedding") and response.embedding:
                    results.append(list(response.embedding.values))
                else:
                    results.append(list(response.embeddings[0].values))
        logger.info(f"Embedding batch complete ({len(results)} facts) via Gemini")
        return results
