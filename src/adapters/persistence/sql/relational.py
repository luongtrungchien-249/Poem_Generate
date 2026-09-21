"""`RelationalRepository` và `CacheRepository` trên SQLAlchemy async.

Chạy nguyên xi trên `sqlite+aiosqlite` lẫn `postgresql+asyncpg` — xem `engine.py`.
"""

from __future__ import annotations

import json
import time

from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncEngine

from contracts.chat import Message
from contracts.chunk import Document
from contracts.feedback import FeedbackRecord
from domain.conversation.tenant import TenantScope

from .bang import bo_nho_dem, phan_hoi, tai_lieu, tin_nhan


class SqlRelationalRepository:
    """Kho quan hệ bền vững, cô lập tenant bằng khoá chính."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    # ---- tin nhắn ----------------------------------------------------------

    async def save_message(self, scope: TenantScope, session_id: str, message: Message) -> None:
        async with self._engine.begin() as conn:
            # Lấy số thứ tự kế tiếp và ghi TRONG CÙNG một giao dịch. Tách ra hai
            # giao dịch thì hai tiến trình có thể đọc cùng một số rồi cùng ghi,
            # và một trong hai mất tin nhắn.
            ke_tiep = await conn.scalar(
                select(func.coalesce(func.max(tin_nhan.c.thu_tu), -1) + 1).where(
                    tin_nhan.c.tenant_id == scope.tenant_id,
                    tin_nhan.c.session_id == session_id,
                )
            )
            await conn.execute(
                insert(tin_nhan).values(
                    tenant_id=scope.tenant_id,
                    session_id=session_id,
                    thu_tu=int(ke_tiep or 0),
                    noi_dung=message.model_dump_json(),
                )
            )

    async def get_messages(
        self, scope: TenantScope, session_id: str, limit: int = 50
    ) -> list[Message]:
        async with self._engine.connect() as conn:
            hang = (
                await conn.execute(
                    select(tin_nhan.c.noi_dung)
                    .where(
                        tin_nhan.c.tenant_id == scope.tenant_id,
                        tin_nhan.c.session_id == session_id,
                    )
                    # Lấy N bản MỚI NHẤT rồi đảo lại. Lấy N bản ĐẦU rồi cắt đuôi sẽ
                    # trả về phần cũ nhất — sai hẳn nghĩa của "recent".
                    .order_by(tin_nhan.c.thu_tu.desc())
                    .limit(limit)
                )
            ).all()
        return [Message(**json.loads(r[0])) for r in reversed(hang)]

    # ---- tài liệu ----------------------------------------------------------

    async def save_document_meta(self, scope: TenantScope, doc: Document) -> None:
        # Ghi đè tenant theo scope: không tin trường trong payload do client gửi.
        ghi = doc.model_copy(update={"tenant_id": scope.tenant_id})
        async with self._engine.begin() as conn:
            # Không dùng UPSERT riêng của từng dialect (`ON CONFLICT` của Postgres,
            # `INSERT OR REPLACE` của SQLite) — hai nhánh mã thì nhánh Postgres
            # không có test nào chạy qua. Xoá-rồi-chèn đúng như nhau ở cả hai.
            await conn.execute(
                delete(tai_lieu).where(
                    tai_lieu.c.tenant_id == scope.tenant_id, tai_lieu.c.doc_id == doc.id
                )
            )
            await conn.execute(
                insert(tai_lieu).values(
                    tenant_id=scope.tenant_id, doc_id=doc.id, noi_dung=ghi.model_dump_json()
                )
            )

    async def get_document_meta(self, scope: TenantScope, doc_id: str) -> Document | None:
        async with self._engine.connect() as conn:
            hang = await conn.scalar(
                select(tai_lieu.c.noi_dung).where(
                    tai_lieu.c.tenant_id == scope.tenant_id, tai_lieu.c.doc_id == doc_id
                )
            )
        return Document(**json.loads(hang)) if hang else None

    # ---- phản hồi ----------------------------------------------------------

    async def save_feedback(self, scope: TenantScope, feedback: FeedbackRecord) -> None:
        async with self._engine.begin() as conn:
            ke_tiep = await conn.scalar(
                select(func.coalesce(func.max(phan_hoi.c.thu_tu), -1) + 1).where(
                    phan_hoi.c.tenant_id == scope.tenant_id
                )
            )
            await conn.execute(
                insert(phan_hoi).values(
                    tenant_id=scope.tenant_id,
                    thu_tu=int(ke_tiep or 0),
                    noi_dung=feedback.model_dump_json(),
                )
            )

    async def get_feedbacks(self, scope: TenantScope, limit: int = 100) -> list[FeedbackRecord]:
        async with self._engine.connect() as conn:
            hang = (
                await conn.execute(
                    select(phan_hoi.c.noi_dung)
                    .where(phan_hoi.c.tenant_id == scope.tenant_id)
                    .order_by(phan_hoi.c.thu_tu.desc())
                    .limit(limit)
                )
            ).all()
        return [FeedbackRecord(**json.loads(r[0])) for r in reversed(hang)]


class SqlCacheRepository:
    """Bộ nhớ đệm bền vững, TTL bằng mốc hết hạn tuyệt đối."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def get(self, key: str) -> str | None:
        async with self._engine.begin() as conn:
            hang = (
                await conn.execute(
                    select(bo_nho_dem.c.gia_tri, bo_nho_dem.c.het_han).where(
                        bo_nho_dem.c.khoa == key
                    )
                )
            ).first()
            if not hang:
                return None
            gia_tri, het_han = hang
            if float(het_han) <= time.time():
                # Dọn ngay khi phát hiện: để lại thì bảng phình mãi bằng rác hết hạn,
                # và không có tiến trình nào khác đi dọn hộ.
                await conn.execute(delete(bo_nho_dem).where(bo_nho_dem.c.khoa == key))
                return None
            return str(gia_tri)

    async def set(self, key: str, value: str, ttl_seconds: int = 3600) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(delete(bo_nho_dem).where(bo_nho_dem.c.khoa == key))
            await conn.execute(
                insert(bo_nho_dem).values(
                    khoa=key, gia_tri=value, het_han=time.time() + ttl_seconds
                )
            )

    async def delete(self, key: str) -> bool:
        async with self._engine.begin() as conn:
            kq = await conn.execute(delete(bo_nho_dem).where(bo_nho_dem.c.khoa == key))
        return bool(kq.rowcount)
