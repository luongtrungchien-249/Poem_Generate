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


@pytest.fixture(params=["sqlite", "postgres"])
async def isolated_sql_dsn(request: pytest.FixtureRequest, tmp_path):
    """Only reset explicitly named test databases, never DATABASE_URL/.env."""
    import os

    from sqlalchemy import text
    from sqlalchemy.engine import make_url

    from adapters.persistence.sql.bang import metadata
    from adapters.persistence.sql.engine import dung_dsn_sqlite, tao_engine

    if request.param == "sqlite":
        yield dung_dsn_sqlite(tmp_path / "isolated.sqlite3")
        return
    dsn = os.environ.get("TEST_DATABASE_URL", "")
    if not dsn:
        pytest.skip("TEST_DATABASE_URL chưa trỏ tới PostgreSQL test riêng")
    url = make_url(dsn)
    if not url.drivername.startswith("postgresql") or not (url.database or "").startswith(
        "poem_improve_test_"
    ):
        pytest.fail(
            "TEST_DATABASE_URL chỉ nhận PostgreSQL DB tên poem_improve_test_*; không dùng DB thật"
        )
    engine = tao_engine(dsn)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(metadata.drop_all)
            await connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
    finally:
        await engine.dispose()
    yield dsn
