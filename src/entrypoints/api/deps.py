"""Dependency của FastAPI: lấy container đã dựng trong lifespan, không tự dựng lại."""

from __future__ import annotations

from fastapi import Request

from bootstrap.container import AppContainer
from bootstrap.container import get_container as _process_container


def get_container(request: Request) -> AppContainer:
    container: AppContainer | None = getattr(request.app.state, "container", None)
    if container is None:
        # Ứng dụng được tạo ngoài lifespan (một số kịch bản test) — dùng container tiến trình.
        return _process_container()
    return container


__all__ = ["AppContainer", "get_container"]
