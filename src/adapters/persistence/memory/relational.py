"""Kho quan hệ in-memory — cho dev và test.

⚠️ MẤT KHI RESTART, và mỗi tiến trình một bản riêng. Bản bền vững là
`adapters/persistence/sqlite/` (G9). Bản Postgres vẫn là Bước 5 — ADR-0003.

CÔ LẬP TENANT: mọi khoá đều mang tenant_id ở đầu. Nhờ vậy hai tenant không thể
đụng vào dữ liệu của nhau kể cả khi trùng `session_id` — và `session_id` thì rất
hay trùng, vì client tự đặt.
"""

from contracts.chat import Message
from contracts.chunk import Document
from contracts.feedback import FeedbackRecord
from domain.conversation.tenant import TenantScope


class InMemoryRelationalRepository:
    """In-memory implementation for testing and development."""

    def __init__(self) -> None:
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
        self._sessions.setdefault(self._khoa(scope, session_id), []).append(message)

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
