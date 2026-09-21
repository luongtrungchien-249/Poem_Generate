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
from contracts.feedback import FeedbackRecord
from domain.conversation.tenant import TenantScope


class RelationalRepository(Protocol):
    async def save_message(self, scope: TenantScope, session_id: str, message: Message) -> None: ...
    async def get_messages(
        self, scope: TenantScope, session_id: str, limit: int = 50
    ) -> list[Message]: ...
    async def save_document_meta(self, scope: TenantScope, doc: Document) -> None: ...
    async def get_document_meta(self, scope: TenantScope, doc_id: str) -> Document | None: ...
    async def save_feedback(self, scope: TenantScope, feedback: FeedbackRecord) -> None: ...
    async def get_feedbacks(self, scope: TenantScope, limit: int = 100) -> list[FeedbackRecord]: ...


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
