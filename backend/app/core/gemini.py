"""Gemini client rotation for independently quota-limited API keys."""

import logging
import time
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
    """Use backup Gemini keys only for transient quota or service failures.

    Rotation strategy:
    - Round 1 (immediate): cycle through all keys with no inter-key delay.
    - Round 2+: cycle through all keys again with exponential inter-round backoff
      (5 s, 10 s) so that transient 503 "high demand" spikes can subside
      before all keys are declared exhausted.
    - Non-rotatable errors (auth failures, bad requests) raise immediately.
    """

    # Inter-round wait schedule in seconds: round 1 = no wait, round 2 = 5s, round 3 = 10s
    _ROUND_WAIT_SECONDS: list[int] = [0, 5, 10]

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
        """Execute *operation* with key rotation and multi-round exponential backoff.

        Rounds are separated by an increasing sleep so Gemini demand spikes
        have time to clear before all keys are declared exhausted.
        """
        n_keys = len(self._clients)
        max_rounds = len(self._ROUND_WAIT_SECONDS)
        last_error: Exception | None = None

        for round_idx in range(max_rounds):
            wait = self._ROUND_WAIT_SECONDS[round_idx]
            if wait > 0:
                logger.warning(
                    "Gemini pool: all %d keys returned transient errors in round %d; "
                    "waiting %ds before retry round %d",
                    n_keys,
                    round_idx,
                    wait,
                    round_idx + 1,
                )
                time.sleep(wait)

            for attempt in range(n_keys):
                try:
                    return operation(self.client)
                except Exception as exc:
                    last_error = exc
                    is_last_chance = (
                        attempt == n_keys - 1 and round_idx == max_rounds - 1
                    )
                    if not _should_rotate_key(exc) or is_last_chance:
                        raise
                    previous_index = self._active_index
                    self._active_index = (self._active_index + 1) % n_keys
                    logger.warning(
                        "Gemini request received a transient error; switching from configured key %d to key %d",
                        previous_index + 1,
                        self._active_index + 1,
                    )

        raise RuntimeError("Gemini client pool exhausted") from last_error
