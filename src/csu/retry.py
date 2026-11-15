"""Retry/backoff helper for throttling (HTTP 429) and transient failures.

No third-party dependency; ``sleep`` is injectable so tests run instantly.
"""
from __future__ import annotations
import time
from typing import Callable, Optional, TypeVar

T = TypeVar("T")


def retry(fn: Callable[[], T], *, attempts: int = 5, base_delay: float = 0.5,
          max_delay: float = 8.0, is_transient: Optional[Callable[[Exception], bool]] = None,
          sleep: Callable[[float], None] = time.sleep) -> T:
    last: Optional[Exception] = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - classify then re-raise
            last = exc
            transient = True if is_transient is None else is_transient(exc)
            if not transient or i == attempts - 1:
                raise
            sleep(min(max_delay, base_delay * (2 ** i)))
    assert last is not None
    raise last
