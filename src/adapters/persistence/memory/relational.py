"""Kho quan hệ in-memory — cho dev và test.

⚠️ MẤT KHI RESTART, và mỗi tiến trình một bản riêng. Bản bền vững là
`adapters/persistence/sqlite/` (G9). Bản Postgres vẫn là Bước 5 — ADR-0003.

CÔ LẬP TENANT: mọi khoá đều mang tenant_id ở đầu. Nhờ vậy hai tenant không thể
đụng vào dữ liệu của nhau kể cả khi trùng `session_id` — và `session_id` thì rất
hay trùng, vì client tự đặt.
"""

import time
import uuid
from datetime import UTC, datetime

from contracts.chat import Message
from contracts.chunk import Document
from contracts.conversation import Conversation
from contracts.feedback import FeedbackRecord
from domain.conversation.tenant import TenantScope


class InMemoryRelationalRepository:
    """In-memory implementation for testing and development."""

    def __init__(self) -> None:
        self._hoi_thoai: dict[tuple[str, str], Conversation] = {}
        self._sessions: dict[tuple[str, str], list[Message]] = {}
        self._documents: dict[tuple[str, str], Document] = {}
        self._feedbacks: dict[str, list[FeedbackRecord]] = {}

    @staticmethod
    def _khoa(scope: TenantScope, ma: str) -> tuple[str, str]:
        """Tenant nằm TRONG khoá, không phải một bộ lọc chạy sau.

        Lọc sau thì quên một chỗ là rò; khoá gộp thì không có chỗ nào để quên.
        """
        return (scope.tenant_id, ma)

    async def save_message(self, scope: TenantScope, session_id: str, message: Message) -> None:
        khoa = self._khoa(scope, session_id)
        self._sessions.setdefault(khoa, []).append(message)
        # Làm mới hội thoại cùng mã — xem docstring của port. Không có hội thoại
        # nào mang mã này thì bỏ qua: `session_id` không bắt buộc là hội thoại.
        c = self._hoi_thoai.get(khoa)
        if c is not None:
            self._hoi_thoai[khoa] = c.model_copy(
                update={"cap_nhat_luc": datetime.now(tz=UTC)}
            )

    async def dat_tieu_de_neu_trong(
        self, scope: TenantScope, conversation_id: str, tieu_de: str
    ) -> None:
        if not tieu_de:
            return
        khoa = self._khoa(scope, conversation_id)
        c = self._hoi_thoai.get(khoa)
        if c is not None and not c.tieu_de:
            self._hoi_thoai[khoa] = c.model_copy(update={"tieu_de": tieu_de})

    async def get_messages(
        self, scope: TenantScope, session_id: str, limit: int = 50
    ) -> list[Message]:
        return self._sessions.get(self._khoa(scope, session_id), [])[-limit:]

    async def save_document_meta(self, scope: TenantScope, doc: Document) -> None:
        # Ghi đè tenant theo scope: không tin trường trong payload do client gửi.
        self._documents[self._khoa(scope, doc.id)] = doc.model_copy(
            update={"tenant_id": scope.tenant_id}
        )

    async def get_document_meta(self, scope: TenantScope, doc_id: str) -> Document | None:
        return self._documents.get(self._khoa(scope, doc_id))

    async def save_feedback(self, scope: TenantScope, feedback: FeedbackRecord) -> None:
        self._feedbacks.setdefault(scope.tenant_id, []).append(feedback)

    async def get_feedbacks(self, scope: TenantScope, limit: int = 100) -> list[FeedbackRecord]:
        return self._feedbacks.get(scope.tenant_id, [])[-limit:]

    # ---- hội thoại ---------------------------------------------------------

    async def tao_hoi_thoai(
        self, scope: TenantScope, tieu_de: str = "", model: str = ""
    ) -> Conversation:
        bay_gio = time.time()
        c = Conversation(
            conversation_id=f"conv_{uuid.uuid4().hex[:12]}",
            tieu_de=tieu_de,
            model=model,
            tao_luc=datetime.fromtimestamp(bay_gio, tz=UTC),
            cap_nhat_luc=datetime.fromtimestamp(bay_gio, tz=UTC),
        )
        self._hoi_thoai[self._khoa(scope, c.conversation_id)] = c
        return c

    async def danh_sach_hoi_thoai(
        self, scope: TenantScope, limit: int = 50
    ) -> list[Conversation]:
        cua_tenant = [
            c for (t, _), c in self._hoi_thoai.items() if t == scope.tenant_id
        ]
        # Mới nhất lên đầu: danh sách hội thoại luôn được đọc từ trên xuống.
        # `conversation_id` là khoá phụ để phá thế hoà — xem bản SQL.
        cua_tenant.sort(key=lambda c: (c.cap_nhat_luc, c.conversation_id), reverse=True)
        return [
            c.model_copy(
                update={"so_tin_nhan": len(self._sessions.get(self._khoa(scope, c.conversation_id), []))}
            )
            for c in cua_tenant[:limit]
        ]

    async def lay_hoi_thoai(
        self, scope: TenantScope, conversation_id: str
    ) -> Conversation | None:
        c = self._hoi_thoai.get(self._khoa(scope, conversation_id))
        if c is None:
            return None
        return c.model_copy(
            update={"so_tin_nhan": len(self._sessions.get(self._khoa(scope, conversation_id), []))}
        )

    async def sua_hoi_thoai(
        self,
        scope: TenantScope,
        conversation_id: str,
        *,
        tieu_de: str | None = None,
        model: str | None = None,
    ) -> Conversation | None:
        khoa = self._khoa(scope, conversation_id)
        c = self._hoi_thoai.get(khoa)
        if c is None:
            return None
        thay: dict[str, object] = {"cap_nhat_luc": datetime.now(tz=UTC)}
        if tieu_de is not None:
            thay["tieu_de"] = tieu_de
        if model is not None:
            thay["model"] = model
        moi = c.model_copy(update=thay)
        self._hoi_thoai[khoa] = moi
        return moi

    async def xoa_hoi_thoai(self, scope: TenantScope, conversation_id: str) -> bool:
        khoa = self._khoa(scope, conversation_id)
        co = self._hoi_thoai.pop(khoa, None) is not None
        # Xoá luôn tin nhắn: để lại là tạo dữ liệu mồ côi.
        self._sessions.pop(khoa, None)
        return co
