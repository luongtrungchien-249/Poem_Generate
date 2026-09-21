"""`VectorRepository` bền vững trên SQL — vector và BM25.

════ 🩸 ĐÍNH CHÍNH MỘT LẬP LUẬN SAI CỦA CHÍNH TÔI ════

Ở G12 tôi từ chối làm kho vector trên SQL với lý do:

    *"lưu vector trong SQL thường thì mỗi lần tìm phải quét toàn bảng và tự tính
    cosine — chép lại in-memory nhưng chậm hơn."*

Vế "chậm hơn" đúng. Vế "chép lại in-memory" **sai**, và sai ở chỗ quan trọng nhất:

    in-memory   MẤT khi restart · MỖI TIẾN TRÌNH một bản
    SQL         BỀN VỮNG        · DÙNG CHUNG giữa các tiến trình

Đó đúng là hai vấn đề tôi đã bỏ công sửa cho kho quan hệ ở G9 và cho bộ đếm ở
G12.2. Bỏ qua chúng ở kho vector chỉ vì tốc độ là đánh đổi sai hạng: tài liệu đã
nạp biến mất sau mỗi lần khởi động lại, và hai worker thấy hai kho khác nhau.

════ QUÉT TOÀN BẢNG CÓ ĐỦ KHÔNG ════

Có, trong phạm vi dự án này. Cosine trên 10.000 vector 64 chiều là ~640.000 phép
nhân — vài chục mili-giây. Kho thơ mẫu hiện có 300 bài.

`pgvector` và Qdrant giải bài toán KHÁC: **tìm gần đúng (ANN)** khi số vector lên
hàng triệu. Đó là tối ưu cho QUY MÔ, không phải sửa lỗi đúng-sai. Ghi rõ ở đây để
không ai nhầm "chưa có pgvector" thành "kho vector chưa dùng được".

⚠️ NGƯỠNG PHẢI ĐỔI HƯỚNG: khi số chunk mỗi tenant vượt ~10⁵, quét toàn bảng bắt
đầu thành vấn đề thật. Lúc đó mới cần ANN, và cổng `VectorRepository` không đổi.

════ CÔ LẬP TENANT ════

`tenant_id` nằm trong khoá chính và trong mọi `WHERE`. Quan trọng hơn ở kho vector
so với kho quan hệ: một truy vấn quên lọc tenant ở đây không báo lỗi, nó chỉ **trả
về tài liệu của người khác** kèm điểm tương đồng trông rất thuyết phục.
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncEngine

from contracts.chunk import EnrichedChunk, RetrievalResult
from domain.conversation.tenant import TenantScope
from domain.knowledge.similarity import cosine_similarity as _cosine_similarity

from .bang import doan_van


class SqlVectorRepository:
    """Kho vector bền vững. Tìm bằng quét toàn bảng trong phạm vi MỘT tenant."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def insert_chunks(self, scope: TenantScope, chunks: list[EnrichedChunk]) -> None:
        if not chunks:
            return
        async with self._engine.begin() as conn:
            for c in chunks:
                # Ghi ĐÈ tenant theo scope, không tin trường trong payload: một
                # client gửi `tenant_id` của người khác là ghi xuyên tenant.
                ghi = c.model_copy(update={"tenant_id": scope.tenant_id})
                await conn.execute(
                    delete(doan_van).where(
                        doan_van.c.tenant_id == scope.tenant_id, doan_van.c.chunk_id == c.id
                    )
                )
                await conn.execute(
                    insert(doan_van).values(
                        tenant_id=scope.tenant_id,
                        chunk_id=c.id,
                        doc_id=c.doc_id,
                        noi_dung=ghi.model_dump_json(),
                    )
                )

    async def _nap(self, scope: TenantScope) -> list[EnrichedChunk]:
        async with self._engine.connect() as conn:
            hang = (
                await conn.execute(
                    select(doan_van.c.noi_dung).where(doan_van.c.tenant_id == scope.tenant_id)
                )
            ).all()
        return [EnrichedChunk(**json.loads(r[0])) for r in hang]

    @staticmethod
    def _hop_le(chunk: EnrichedChunk, filters: dict[str, Any] | None) -> bool:
        """Tenant đã lọc ở SQL; `filters` chỉ còn cho bộ lọc nghiệp vụ khác."""
        return not (filters and any(chunk.metadata.get(k) != v for k, v in filters.items()))

    @staticmethod
    def _ket_qua(
        cham: list[tuple[float, EnrichedChunk]], top_k: int, nguon: str
    ) -> list[RetrievalResult]:
        cham.sort(key=lambda x: x[0], reverse=True)
        return [
            RetrievalResult(
                chunk_id=c.id, doc_id=c.doc_id, content=c.content,
                score=round(diem, 4), rank=hang, source_type=nguon, metadata=c.metadata,
            )
            for hang, (diem, c) in enumerate(cham[:top_k], start=1)
        ]

    async def search_vector(
        self,
        scope: TenantScope,
        query_vector: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        cham = [
            (_cosine_similarity(query_vector, c.embedding), c)
            for c in await self._nap(scope)
            if c.embedding and self._hop_le(c, filters)
        ]
        return self._ket_qua(cham, top_k, "dense")

    async def search_bm25(
        self,
        scope: TenantScope,
        query_text: str,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        # Cùng phép chấm với bản in-memory, cố ý: hai kho cho ra thứ hạng khác nhau
        # thì đổi kho sẽ lặng lẽ đổi kết quả RAG, và không ai quy được nguyên nhân.
        tu_truy_van = set(query_text.lower().split())
        cham: list[tuple[float, EnrichedChunk]] = []
        for c in await self._nap(scope):
            if not self._hop_le(c, filters):
                continue
            tu_doan = c.content.lower().split()
            if not tu_doan:
                continue
            trung = sum(1 for t in tu_doan if t in tu_truy_van)
            if trung:
                cham.append((trung / len(tu_doan), c))
        return self._ket_qua(cham, top_k, "sparse")
