"""Gemini client rotation for independently quota-limited API keys.

Strategy: three independent free-tier keys provide horizontal capacity.
When one key gets rate-limited (429) or a transient error (5xx), the pool
rotates to the next key so the previous key can cool down while processing
continues.  After one full pass through all keys fails, the error is raised
immediately so callers can skip the item gracefully — there is no point in
hammering every key multiple times for a model-wide 503 demand spike.
"""

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
    """Return whether an API failure warrants trying the next key."""
    status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if status_code in _ROTATABLE_STATUS_CODES:
        return True
    return any(marker in str(exc).lower() for marker in _ROTATABLE_ERROR_MARKERS)


class GeminiClientPool:
    """Rotate through configured Gemini API keys on transient failures.

    When a key hits a per-key rate limit (429) or a transient server error
    (5xx), the pool advances to the next key so the throttled key can recover
    while processing continues on the next key.

    If all configured keys fail in a single pass, the last exception is
    re-raised so the caller can handle it (e.g. skip a page and move on).
    Non-rotatable errors (400 bad request, 401 auth) always raise immediately.
    """

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
        """Generate content, rotating to the next key on transient errors."""
        return self._call(lambda client: client.models.generate_content(**kwargs))

    def embed_content(self, **kwargs: Any) -> Any:
        """Embed content, rotating to the next key on transient errors."""
        return self._call(lambda client: client.models.embed_content(**kwargs))

    def _call(self, operation: Callable[[genai.Client], T]) -> T:
        """Try each key once in sequence; raise after one full pass fails.

        This gives the previously active (throttled) key time to cool down
        while subsequent requests land on the next key.  The inter-call pacing
        in ExtractionService (INTER_CALL_DELAY_SECONDS) is what provides the
        actual recovery window — not repeated retries inside this pool.
        """
        n_keys = len(self._clients)
        last_error: Exception | None = None

        for attempt in range(n_keys):
            try:
                return operation(self.client)
            except Exception as exc:
                last_error = exc
                if not _should_rotate_key(exc):
                    # Non-transient error (auth failure, bad request) — raise immediately
                    raise
                if attempt < n_keys - 1:
                    previous_index = self._active_index
                    self._active_index = (self._active_index + 1) % n_keys
                    logger.warning(
                        "Gemini key %d returned a transient error (%s); rotating to key %d",
                        previous_index + 1,
                        type(exc).__name__,
                        self._active_index + 1,
                    )
                # else: last key also failed — fall through to raise below

        raise last_error  # type: ignore[misc]
