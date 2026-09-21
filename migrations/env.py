"""Môi trường Alembic — migration cho kho SQL.

════ VÌ SAO CẦN ALEMBIC KHI ĐÃ CÓ `create_all` ════

`engine.tao_bang()` gọi `metadata.create_all`, và nó chỉ làm được đúng một việc:
**tạo bảng còn thiếu**. Nó KHÔNG biết gì về:

    - đổi kiểu một cột đã có
    - thêm cột NOT NULL vào bảng đang có dữ liệu
    - đổi tên, tách bảng, chuyển dữ liệu

Với dev và SQLite thì đủ, vì xoá tệp đi tạo lại là xong. Với production thì không:
`create_all` **im lặng bỏ qua** mọi bảng đã tồn tại, nên một cột đổi kiểu sẽ không
bao giờ được áp — và lỗi chỉ lộ ra lúc ghi, ở xa nơi gây ra nó.

════ DSN KHÔNG NẰM TRONG TỆP COMMIT ĐƯỢC ════

`alembic.ini` để trống `sqlalchemy.url`. DSN có thể chứa mật khẩu, và nguyên tắc
của repo này là bí mật chỉ ở biến môi trường (xem `bootstrap/settings.py`).

Thứ tự ưu tiên: `-x dsn=...` trên dòng lệnh → `DATABASE_URL` → SQLite cục bộ.

════ CHẠY ĐƯỢC TRÊN CẢ HAI DIALECT ════

`render_as_batch=True` là bắt buộc cho SQLite: SQLite không có `ALTER COLUMN`, nên
Alembic phải dựng bảng mới, chép dữ liệu, rồi đổi tên. Bật cờ này cho cả hai dialect
để một migration viết ra chạy được ở cả hai — nếu chỉ bật cho SQLite thì có thể viết
ra migration chạy trên Postgres mà hỏng trên SQLite, và CI sẽ không bắt được.
"""

from __future__ import annotations

import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy.engine import Connection

GOC = Path(__file__).resolve().parents[1]
if str(GOC / "src") not in sys.path:
    sys.path.insert(0, str(GOC / "src"))

from adapters.persistence.sql.bang import metadata  # noqa: E402
from adapters.persistence.sql.engine import dung_dsn_sqlite, tao_engine  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata


def _dsn() -> str:
    tu_dong_lenh = context.get_x_argument(as_dictionary=True).get("dsn")
    return (
        tu_dong_lenh
        or os.environ.get("DATABASE_URL")
        or dung_dsn_sqlite(GOC / "data" / "app.sqlite3")
    )


def chay_offline() -> None:
    """Sinh SQL ra màn hình, không kết nối.

    Dùng khi người vận hành muốn XEM câu lệnh trước khi cho chạy trên production —
    một thói quen đáng giữ với mọi thay đổi lược đồ.
    """
    context.configure(
        url=_dsn(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _chay_migration(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
        # So sánh KIỂU cột, không chỉ so sự tồn tại. Tắt thì một cột đổi từ
        # String(128) sang String(256) sẽ không sinh migration nào.
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def _chay_async() -> None:
    engine = tao_engine(_dsn())
    async with engine.connect() as conn:
        await conn.run_sync(_chay_migration)
    await engine.dispose()


def chay_online() -> None:
    asyncio.run(_chay_async())


if context.is_offline_mode():
    chay_offline()
else:
    chay_online()
