from typing import Any

from contracts.chunk import EnrichedChunk, RetrievalResult
from domain.conversation.tenant import TenantScope
from domain.knowledge.similarity import cosine_similarity as _cosine_similarity


class InMemoryVectorRepository:
    """In-memory Vector and BM25 repository supporting exact filtering.

    🩸 LỖI ĐÃ SỬA 21/09/2026 — CÔ LẬP TENANT HỎNG HOÀN TOÀN.

    Bản trước nhận tenant qua `filters={"tenant_id": ...}` rồi lọc trên
    `chunk.metadata`. Nhưng `tenant_id` là **field của `Chunk`**, không nằm trong
    `metadata` — nên `chunk.metadata.get("tenant_id")` luôn trả None, không khớp
    giá trị nào, và **mọi chunk đều bị loại: RAG luôn trả về rỗng.**

    Hỏng theo hướng im lặng: RAG rỗng trông như "không tìm thấy tài liệu", không
    như "bộ lọc sai". Và nếu ai đó sửa nhầm thành bỏ lọc, nó lật sang hướng ngược
    lại — rò dữ liệu giữa các tenant.

    Nay tenant đi qua `TenantScope` ở tham số đầu, và lọc trên `chunk.tenant_id`.
    """

    def __init__(self) -> None:
        self._chunks: dict[str, EnrichedChunk] = {}

    async def insert_chunks(self, scope: TenantScope, chunks: list[EnrichedChunk]) -> None:
        for c in chunks:
            # Ghi ĐÈ tenant theo scope, không tin trường trong payload: một client
            # gửi `tenant_id` của người khác thì đó là ghi xuyên tenant.
            self._chunks[c.id] = c.model_copy(update={"tenant_id": scope.tenant_id})

    def _hop_le(self, chunk: EnrichedChunk, scope: TenantScope, filters: dict | None) -> bool:
        """Tenant lọc trên FIELD; `filters` chỉ còn cho bộ lọc nghiệp vụ khác."""
        if not scope.khop(chunk.tenant_id):
            return False
        return not (filters and any(chunk.metadata.get(k) != v for k, v in filters.items()))

    async def search_vector(
        self,
        scope: TenantScope,
        query_vector: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        scored: list[tuple[float, EnrichedChunk]] = []
        for chunk in self._chunks.values():
            if not self._hop_le(chunk, scope, filters):
                continue
            if not chunk.embedding:
                continue
            sim = _cosine_similarity(query_vector, chunk.embedding)
            scored.append((sim, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        results: list[RetrievalResult] = []
        for rank, (score, chunk) in enumerate(scored[:top_k], start=1):
            results.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    doc_id=chunk.doc_id,
                    content=chunk.content,
                    score=round(score, 4),
                    rank=rank,
                    source_type="dense",
                    metadata=chunk.metadata,
                )
            )
        return results

    async def search_bm25(
        self,
        scope: TenantScope,
        query_text: str,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        query_tokens = set(query_text.lower().split())
        scored: list[tuple[float, EnrichedChunk]] = []

        for chunk in self._chunks.values():
            if not self._hop_le(chunk, scope, filters):
                continue
            chunk_tokens = chunk.content.lower().split()
            if not chunk_tokens:
                continue
            matches = sum(1 for t in chunk_tokens if t in query_tokens)
            score = matches / (len(chunk_tokens) ** 0.5)
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        results: list[RetrievalResult] = []
        for rank, (score, chunk) in enumerate(scored[:top_k], start=1):
            results.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    doc_id=chunk.doc_id,
                    content=chunk.content,
                    score=round(score, 4),
                    rank=rank,
                    source_type="sparse",
                    metadata=chunk.metadata,
                )
            )
        return results
