"""`RelationalRepository` và `CacheRepository` trên SQLAlchemy async.

Chạy nguyên xi trên `sqlite+aiosqlite` lẫn `postgresql+asyncpg` — xem `engine.py`.
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, func, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncEngine

from contracts.chat import Message
from contracts.chunk import Document
from contracts.conversation import Conversation
from contracts.feedback import FeedbackRecord
from domain.conversation.tenant import TenantScope

from .bang import bo_nho_dem, hoi_thoai, phan_hoi, tai_lieu, tin_nhan


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
            # Làm mới hội thoại TRONG CÙNG giao dịch. Không có hàng nào khớp thì
            # UPDATE này không làm gì — `session_id` của đường chat không bắt
            # buộc phải là một hội thoại.
            await conn.execute(
                update(hoi_thoai)
                .where(
                    hoi_thoai.c.tenant_id == scope.tenant_id,
                    hoi_thoai.c.conversation_id == session_id,
                )
                .values(cap_nhat_luc=time.time())
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

    # ---- hội thoại ---------------------------------------------------------

    async def tao_hoi_thoai(
        self, scope: TenantScope, tieu_de: str = "", model: str = ""
    ) -> Conversation:
        ma = f"conv_{uuid.uuid4().hex[:12]}"
        bay_gio = time.time()
        async with self._engine.begin() as conn:
            await conn.execute(
                insert(hoi_thoai).values(
                    tenant_id=scope.tenant_id, conversation_id=ma, tieu_de=tieu_de,
                    model=model, tao_luc=bay_gio, cap_nhat_luc=bay_gio,
                )
            )
        return Conversation(
            conversation_id=ma, tieu_de=tieu_de, model=model,
            tao_luc=datetime.fromtimestamp(bay_gio, tz=UTC),
            cap_nhat_luc=datetime.fromtimestamp(bay_gio, tz=UTC),
        )

    async def _dem_tin_nhan(self, conn: object, scope: TenantScope, ma: str) -> int:
        n = await conn.scalar(  # type: ignore[attr-defined]
            select(func.count()).select_from(tin_nhan).where(
                tin_nhan.c.tenant_id == scope.tenant_id, tin_nhan.c.session_id == ma
            )
        )
        return int(n or 0)

    async def danh_sach_hoi_thoai(
        self, scope: TenantScope, limit: int = 50
    ) -> list[Conversation]:
        async with self._engine.connect() as conn:
            hang = (
                await conn.execute(
                    select(hoi_thoai)
                    .where(hoi_thoai.c.tenant_id == scope.tenant_id)
                    # Mới nhất lên đầu: danh sách luôn được đọc từ trên xuống.
                    # `conversation_id` là khoá phụ để phá thế hoà: hai hội thoại
                    # tạo trong cùng một tick có `cap_nhat_luc` bằng nhau, và khi
                    # đó thứ tự trả về là tuỳ ý — nghĩa là sidebar có thể đổi thứ
                    # tự giữa hai lần tải mà không có gì thay đổi.
                    .order_by(hoi_thoai.c.cap_nhat_luc.desc(), hoi_thoai.c.conversation_id.desc())
                    .limit(limit)
                )
            ).all()
            ra = []
            for h in hang:
                ra.append(_sang_conversation(h, await self._dem_tin_nhan(conn, scope, h.conversation_id)))
        return ra

    async def lay_hoi_thoai(
        self, scope: TenantScope, conversation_id: str
    ) -> Conversation | None:
        async with self._engine.connect() as conn:
            h = (
                await conn.execute(
                    select(hoi_thoai).where(
                        hoi_thoai.c.tenant_id == scope.tenant_id,
                        hoi_thoai.c.conversation_id == conversation_id,
                    )
                )
            ).first()
            if h is None:
                return None
            return _sang_conversation(h, await self._dem_tin_nhan(conn, scope, conversation_id))

    async def sua_hoi_thoai(
        self,
        scope: TenantScope,
        conversation_id: str,
        *,
        tieu_de: str | None = None,
        model: str | None = None,
    ) -> Conversation | None:
        gia_tri: dict[str, object] = {"cap_nhat_luc": time.time()}
        if tieu_de is not None:
            gia_tri["tieu_de"] = tieu_de
        if model is not None:
            gia_tri["model"] = model
        async with self._engine.begin() as conn:
            kq = await conn.execute(
                update(hoi_thoai)
                .where(
                    hoi_thoai.c.tenant_id == scope.tenant_id,
                    hoi_thoai.c.conversation_id == conversation_id,
                )
                .values(**gia_tri)
            )
            if not kq.rowcount:
                return None
        return await self.lay_hoi_thoai(scope, conversation_id)

    async def dat_tieu_de_neu_trong(
        self, scope: TenantScope, conversation_id: str, tieu_de: str
    ) -> None:
        if not tieu_de:
            return
        async with self._engine.begin() as conn:
            # "Đang trống" là một phần của WHERE, không phải một lần đọc trước đó:
            # cơ sở dữ liệu tự bảo đảm chỉ một yêu cầu thắng.
            await conn.execute(
                update(hoi_thoai)
                .where(
                    hoi_thoai.c.tenant_id == scope.tenant_id,
                    hoi_thoai.c.conversation_id == conversation_id,
                    or_(hoi_thoai.c.tieu_de == "", hoi_thoai.c.tieu_de.is_(None)),
                )
                .values(tieu_de=tieu_de)
            )

    async def xoa_hoi_thoai(self, scope: TenantScope, conversation_id: str) -> bool:
        async with self._engine.begin() as conn:
            kq = await conn.execute(
                delete(hoi_thoai).where(
                    hoi_thoai.c.tenant_id == scope.tenant_id,
                    hoi_thoai.c.conversation_id == conversation_id,
                )
            )
            # Xoá tin nhắn TRONG CÙNG giao dịch: tách ra thì một lỗi ở giữa để lại
            # tin nhắn mồ côi mà người dùng tưởng đã xoá.
            await conn.execute(
                delete(tin_nhan).where(
                    tin_nhan.c.tenant_id == scope.tenant_id,
                    tin_nhan.c.session_id == conversation_id,
                )
            )
        return bool(kq.rowcount)


def _sang_conversation(hang: object, so_tin_nhan: int = 0) -> Conversation:
    return Conversation(
        conversation_id=hang.conversation_id,  # type: ignore[attr-defined]
        tieu_de=hang.tieu_de or "",  # type: ignore[attr-defined]
        model=hang.model or "",  # type: ignore[attr-defined]
        tao_luc=datetime.fromtimestamp(float(hang.tao_luc), tz=UTC),  # type: ignore[attr-defined]
        cap_nhat_luc=datetime.fromtimestamp(float(hang.cap_nhat_luc), tz=UTC),  # type: ignore[attr-defined]
        so_tin_nhan=so_tin_nhan,
    )


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
