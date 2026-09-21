"""Dựng engine async — một chỗ duy nhất biết về dialect.

════ HAI DIALECT, VÀ CHỖ DUY NHẤT CHÚNG KHÁC NHAU ════

    sqlite+aiosqlite://   dev, test, triển khai một tiến trình
    postgresql+asyncpg:// nhiều tiến trình, nhiều worker

Toàn bộ phần còn lại của `adapters/persistence/sql/` **không biết** mình đang chạy
trên dialect nào. Đó là điều khiến adapter Postgres kiểm chứng được: test chạy trên
SQLite, và phần chưa kiểm thu lại chỉ còn phương ngữ SQL — thứ SQLAlchemy lo.

════ MỘT KHÁC BIỆT THẬT, PHẢI XỬ LÝ ════

SQLite mặc định KHÔNG cho hai kết nối ghi đồng thời, và trong asyncio thì điều đó
thành treo chứ không thành lỗi. `PRAGMA journal_mode=WAL` cho phép đọc song song
với ghi, và `busy_timeout` biến "khoá bận" từ lỗi tức thì thành chờ có giới hạn.

Postgres không cần hai thứ đó, nên chúng chỉ bật cho SQLite — và đó là toàn bộ
phần biết-dialect của module này.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .bang import metadata

# Chờ tối đa khi tệp SQLite đang bị khoá ghi. 5 giây đủ cho mọi thao tác trong repo
# này (đều là ghi một dòng); dài hơn thì che mất một vấn đề thật về tranh chấp.
SQLITE_BUSY_TIMEOUT_MS = 5000


def la_sqlite(dsn: str) -> bool:
    return dsn.startswith("sqlite")


def dung_dsn_sqlite(duong_dan: str | Path) -> str:
    """Đường dẫn tệp -> DSN async. Tạo sẵn thư mục cha."""
    p = Path(duong_dan)
    p.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite+aiosqlite:///{p.as_posix()}"


def tao_engine(dsn: str) -> AsyncEngine:
    """Engine async cho một DSN bất kỳ trong hai dialect được hỗ trợ."""
    engine = create_async_engine(dsn, future=True)

    if la_sqlite(dsn):

        @event.listens_for(engine.sync_engine, "connect")
        def _pragma(dbapi_conn: object, _rec: object) -> None:
            cur = dbapi_conn.cursor()  # type: ignore[attr-defined]
            cur.execute("PRAGMA journal_mode=WAL")
            cur.execute(f"PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}")
            cur.close()

    return engine


async def tao_bang(engine: AsyncEngine) -> None:
    """Tạo bảng nếu chưa có.

    Đủ cho dev và cho SQLite. Với Postgres ở production thì **migration phải do
    Alembic lo**: `create_all` không biết gì về việc đổi lược đồ trên dữ liệu đã
    có — nó chỉ tạo cái còn thiếu, và im lặng bỏ qua cột đã đổi kiểu.

    ⚠️ Alembic CHƯA được thêm. Ghi ra đây thay vì để người deploy phát hiện lúc
    cần đổi lược đồ lần đầu.
    """
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
