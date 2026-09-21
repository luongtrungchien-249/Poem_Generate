from collections import defaultdict
from typing import Any

from application.ports.embedding import EmbeddingPort
from application.ports.repositories import VectorRepository
from contracts.chunk import RetrievalResult
from domain.conversation.tenant import TenantScope


class HybridRetriever:
    """Combines BM25 keyword search and dense semantic vector search via Reciprocal Rank Fusion (RRF)."""

    def __init__(
        self,
        vector_repo: VectorRepository,
        embedder: EmbeddingPort,
        rrf_k: int = 60,
    ) -> None:
        self.vector_repo = vector_repo
        self.embedder = embedder
        self.rrf_k = rrf_k

    async def retrieve(
        self,
        scope: TenantScope,
        query: str,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        """`scope` đứng ĐẦU và bắt buộc — ADR-0003.

        Trước đây tenant đi qua `filters` như một khoá chuỗi, và nó bị lọc nhầm chỗ
        khiến RAG luôn trả rỗng. `filters` nay chỉ còn cho các bộ lọc NGHIỆP VỤ
        khác; tenant không bao giờ đi qua đó nữa.
        """
        # 1. Generate query embedding
        query_vectors = await self.embedder.embed([query])
        query_vec = query_vectors[0] if query_vectors else []

        # 2. Parallel / sequential search
        dense_results = await self.vector_repo.search_vector(
            scope, query_vec, top_k=top_k * 2, filters=filters
        )
        sparse_results = await self.vector_repo.search_bm25(
            scope, query, top_k=top_k * 2, filters=filters
        )

        # 3. Reciprocal Rank Fusion
        rrf_scores: dict[str, float] = defaultdict(float)
        chunk_map: dict[str, RetrievalResult] = {}

        for rank, res in enumerate(dense_results, start=1):
            rrf_scores[res.chunk_id] += 1.0 / (self.rrf_k + rank)
            chunk_map[res.chunk_id] = res

        for rank, res in enumerate(sparse_results, start=1):
            rrf_scores[res.chunk_id] += 1.0 / (self.rrf_k + rank)
            if res.chunk_id not in chunk_map:
                chunk_map[res.chunk_id] = res

        # Sort by combined RRF score
        sorted_chunk_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        final_results: list[RetrievalResult] = []
        for rank, cid in enumerate(sorted_chunk_ids[:top_k], start=1):
            base_res = chunk_map[cid]
            final_results.append(
                RetrievalResult(
                    chunk_id=base_res.chunk_id,
                    doc_id=base_res.doc_id,
                    content=base_res.content,
                    score=round(rrf_scores[cid], 5),
                    rank=rank,
                    source_type="hybrid_rrf",
                    metadata=base_res.metadata,
                )
            )
        return final_results
