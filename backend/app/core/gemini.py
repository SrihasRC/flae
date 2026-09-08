"""Gemini client rotation for independently quota-limited API keys."""

import logging
from collections.abc import Callable
from typing import Any, TypeVar

from google import genai

from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")
_ROTATABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
_ROTATABLE_ERROR_MARKERS = ("resource_exhausted", "rate limit", "unavailable", "timeout")


def _should_rotate_key(exc: Exception) -> bool:
    """Return whether an API failure is safe to retry with another key."""
    status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if status_code in _ROTATABLE_STATUS_CODES:
        return True
    return any(marker in str(exc).lower() for marker in _ROTATABLE_ERROR_MARKERS)


class GeminiClientPool:
    """Use backup Gemini keys only for transient quota or service failures."""

    def __init__(
        self,
        client: genai.Client | None = None,
        api_keys: list[str] | None = None,
    ) -> None:
        if client is not None:
            self._clients = [client]
        else:
            keys = api_keys if api_keys is not None else settings.gemini_api_keys
            self._clients = [genai.Client(api_key=key) for key in keys]
        if not self._clients:
            self._clients = [genai.Client(api_key="dummy-api-key")]
        self._active_index = 0

    @property
    def client(self) -> genai.Client:
        """Return the currently active SDK client."""
        return self._clients[self._active_index]

    def generate_content(self, **kwargs: Any) -> Any:
        """Generate content, rotating keys only after a transient API failure."""
        return self._call(lambda client: client.models.generate_content(**kwargs))

    def embed_content(self, **kwargs: Any) -> Any:
        """Embed content, rotating keys only after a transient API failure."""
        return self._call(lambda client: client.models.embed_content(**kwargs))

    def _call(self, operation: Callable[[genai.Client], T]) -> T:
        last_error: Exception | None = None
        for attempt in range(len(self._clients)):
            try:
                return operation(self.client)
            except Exception as exc:
                last_error = exc
                if not _should_rotate_key(exc) or attempt == len(self._clients) - 1:
                    raise
                previous_index = self._active_index
                self._active_index = (self._active_index + 1) % len(self._clients)
                logger.warning(
                    "Gemini request received a transient error; switching from configured key %d to key %d",
                    previous_index + 1,
                    self._active_index + 1,
                )
        raise RuntimeError("Gemini client pool exhausted") from last_error
