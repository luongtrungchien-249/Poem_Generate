"""Port quan trắc. Lõi phát ra span qua Protocol này, không gọi thẳng OpenTelemetry."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Protocol


class TracerPort(Protocol):
    @contextmanager
    def span(self, name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
        """Mở một span con và ghi lại thời lượng khi thoát."""
        ...


class NullTracer:
    """Mặc định không làm gì — để lõi chạy được trong test mà không cần hạ tầng."""

    @contextmanager
    def span(self, name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
        yield dict(attributes or {})


__all__ = ["TracerPort", "NullTracer"]
