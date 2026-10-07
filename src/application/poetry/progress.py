"""Application progress reports carry metadata, never draft content."""

from collections.abc import Awaitable, Callable
from typing import Any

ProgressHook = Callable[[str, dict[str, Any]], Awaitable[None]]


async def report(hook: ProgressHook | None, status: str, **metadata: Any) -> None:
    if hook is not None:
        await hook(status, metadata)
