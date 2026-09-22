"""Port lưu trữ. Application chỉ biết các Protocol này, không biết ai hiện thực chúng.

⛔ RÀNG BUỘC CÔ LẬP TENANT — ADR-0003, thi hành 21/09/2026

Mọi phương thức CHẠM DỮ LIỆU NGƯỜI THUÊ phải nhận `TenantScope` ở **tham số đầu
tiên**. Không phải quy ước đặt tên, không phải điều dặn trong review — là chữ ký.

Test `tests/architecture/test_tenant_scope.py` quét AST và cưỡng chế điều này.

Vì sao gắt đến vậy: bản trước truyền tenant qua `filters={"tenant_id": ...}` và lọc
nhầm chỗ (`chunk.metadata` thay vì `chunk.tenant_id`), khiến RAG luôn trả rỗng. Một
`dict` thì gõ sai khoá là rò dữ liệu, gõ sai chỗ là mất hết kết quả — và cả hai đều
im lặng. Một tham số bắt buộc, đúng kiểu, chặn được cả hai.
"""

from __future__ import annotations

from typing import Any, Protocol

from contracts.chat import Message
from contracts.chunk import Document, EnrichedChunk, RetrievalResult
from contracts.conversation import Conversation
from contracts.feedback import FeedbackRecord
from domain.conversation.tenant import TenantScope


class RelationalRepository(Protocol):
    async def save_message(self, scope: TenantScope, session_id: str, message: Message) -> None:
        """Ghi một tin nhắn, VÀ làm mới `cap_nhat_luc` của hội thoại cùng mã.

        Hai việc trong một phương thức là có chủ ý. Danh sách hội thoại sắp xếp
        theo `cap_nhat_luc`, nên nếu việc làm mới là một lời gọi RIÊNG thì mọi
        đường ghi tin nhắn đều phải nhớ gọi nó — và đường nào quên thì cuộc trò
        chuyện đó tụt xuống đáy sidebar dù vừa mới nhắn. Gộp vào đây thì không
        có chỗ nào để quên.

        Không có hội thoại nào mang mã đó thì phần làm mới không làm gì: `session_id`
        của đường chat không bắt buộc phải là một hội thoại.
        """
        ...

    async def dat_tieu_de_neu_trong(
        self, scope: TenantScope, conversation_id: str, tieu_de: str
    ) -> None:
        """Đặt tiêu đề CHỈ KHI nó đang trống.

        Điều kiện "đang trống" nằm trong mệnh đề WHERE chứ không phải một lần đọc
        rồi ghi: đọc trước rồi ghi sau thì hai yêu cầu gửi gần nhau cùng thấy
        trống, và tiêu đề do người dùng tự đặt có thể bị câu đầu tiên ghi đè.
        """
        ...
    async def get_messages(
        self, scope: TenantScope, session_id: str, limit: int = 50
    ) -> list[Message]: ...
    async def save_document_meta(self, scope: TenantScope, doc: Document) -> None: ...
    async def get_document_meta(self, scope: TenantScope, doc_id: str) -> Document | None: ...
    async def save_feedback(self, scope: TenantScope, feedback: FeedbackRecord) -> None: ...
    async def get_feedbacks(self, scope: TenantScope, limit: int = 100) -> list[FeedbackRecord]: ...

    # ---- hội thoại (§15 AI_LLM_Chat_Web_UI_Plan) ---------------------------
    async def tao_hoi_thoai(
        self, scope: TenantScope, tieu_de: str = "", model: str = ""
    ) -> Conversation:
        """Tạo hội thoại mới. `conversation_id` do HIỆN THỰC sinh, không nhận
        từ ngoài — xem `contracts/conversation.py`."""
        ...

    async def danh_sach_hoi_thoai(
        self, scope: TenantScope, limit: int = 50
    ) -> list[Conversation]: ...

    async def lay_hoi_thoai(
        self, scope: TenantScope, conversation_id: str
    ) -> Conversation | None: ...

    async def sua_hoi_thoai(
        self,
        scope: TenantScope,
        conversation_id: str,
        *,
        tieu_de: str | None = None,
        model: str | None = None,
    ) -> Conversation | None: ...

    async def xoa_hoi_thoai(self, scope: TenantScope, conversation_id: str) -> bool:
        """Xoá hội thoại VÀ mọi tin nhắn của nó.

        Xoá siêu dữ liệu mà để lại tin nhắn là tạo ra dữ liệu mồ côi: người dùng
        thấy đã xoá, nhưng nội dung vẫn nằm trong cơ sở dữ liệu.
        """
        ...


class VectorRepository(Protocol):
    async def insert_chunks(self, scope: TenantScope, chunks: list[EnrichedChunk]) -> None: ...
    async def search_vector(
        self,
        scope: TenantScope,
        query_vector: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]: ...
    async def search_bm25(
        self,
        scope: TenantScope,
        query_text: str,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]: ...


class BlobRepository(Protocol):
    async def put_object(self, key: str, data: bytes, content_type: str = "text/plain") -> str: ...
    async def get_object(self, key: str) -> bytes | None: ...
    async def delete_object(self, key: str) -> bool: ...


class CacheRepository(Protocol):
    async def get(self, key: str) -> str | None: ...
    async def set(self, key: str, value: str, ttl_seconds: int = 3600) -> None: ...
    async def delete(self, key: str) -> bool: ...


__all__ = ["RelationalRepository", "VectorRepository", "BlobRepository", "CacheRepository"]
