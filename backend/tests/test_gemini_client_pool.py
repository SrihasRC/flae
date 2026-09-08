from types import SimpleNamespace

import pytest

from app.core.gemini import GeminiClientPool


class RaisingModels:
    def generate_content(self, **_: object) -> object:
        raise RuntimeError("429 RESOURCE_EXHAUSTED")


class SuccessfulModels:
    def generate_content(self, **_: object) -> object:
        return {"result": "ok"}


def test_pool_rotates_after_quota_error() -> None:
    pool = GeminiClientPool(client=SimpleNamespace(models=SuccessfulModels()))  # type: ignore[arg-type]
    pool._clients = [
        SimpleNamespace(models=RaisingModels()),
        SimpleNamespace(models=SuccessfulModels()),
    ]
    pool._active_index = 0

    assert pool.generate_content(model="gemini-3.8-flash", contents="hello") == {"result": "ok"}
    assert pool._active_index == 1


def test_pool_does_not_rotate_for_invalid_request() -> None:
    class InvalidRequestModels:
        def generate_content(self, **_: object) -> object:
            raise RuntimeError("400 INVALID_ARGUMENT")

    pool = GeminiClientPool(client=SimpleNamespace(models=InvalidRequestModels()))  # type: ignore[arg-type]

    with pytest.raises(RuntimeError, match="INVALID_ARGUMENT"):
        pool.generate_content(model="gemini-3.8-flash", contents="hello")
