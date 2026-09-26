"""Cấu hình chung cho toàn bộ test.

Nguyên tắc: test KHÔNG BAO GIỜ được chạm mạng thật. Mọi khoá API trong môi trường
của lập trình viên đều bị vô hiệu ở đây, và provider bị ép về `mock`.
"""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:  # noqa: ARG001
    """Chạy TRƯỚC khi pytest nạp bất kỳ module test nào.

    Phải sớm như vậy: `load_settings` nạp `.env` vào môi trường (không ghi đè biến
    đã có), và vài module test đọc môi trường ngay lúc import — ví dụ `DSN_POSTGRES`
    của test tích hợp. Làm ở fixture thì đã muộn.
    """
    import os

    # Khoá API: LUÔN rỗng. Đặt rỗng chứ không xoá — xoá thì bản trong `.env` quay lại.
    for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"):
        os.environ[key] = ""
    # Hạ tầng: giữ giá trị người chạy TỰ ĐẶT (`DATABASE_URL=... pytest tests/integration`),
    # chỉ chặn bản lấy từ `.env`.
    for key in ("DATABASE_URL", "REDIS_URL", "QDRANT_URL"):
        os.environ.setdefault(key, "")
    os.environ["ENV"] = "dev"
    os.environ["DEFAULT_PROVIDER"] = "mock"
    os.environ["DEFAULT_MODEL"] = "mock-gpt"


@pytest.fixture(autouse=True, scope="session")
def _force_offline_providers() -> None:
    from bootstrap.container import get_container
    from bootstrap.settings import get_settings

    get_settings.cache_clear()
    get_container.cache_clear()
