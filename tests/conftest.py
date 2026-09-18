"""Cấu hình chung cho toàn bộ test.

Nguyên tắc: test KHÔNG BAO GIỜ được chạm mạng thật. Mọi khoá API trong môi trường
của lập trình viên đều bị vô hiệu ở đây, và provider bị ép về `mock`.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True, scope="session")
def _force_offline_providers() -> None:
    import os

    for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DATABASE_URL", "REDIS_URL", "QDRANT_URL"):
        os.environ.pop(key, None)
    os.environ["ENV"] = "dev"
    os.environ["DEFAULT_PROVIDER"] = "mock"
    os.environ["DEFAULT_MODEL"] = "mock-gpt"

    from bootstrap.container import get_container
    from bootstrap.settings import get_settings

    get_settings.cache_clear()
    get_container.cache_clear()
