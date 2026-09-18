from typing import Any

from contracts.chunk import EnrichedChunk, RetrievalResult
from domain.knowledge.similarity import cosine_similarity as _cosine_similarity


class InMemoryVectorRepository:
    """In-memory Vector and BM25 repository supporting exact filtering."""

    def __init__(self) -> None:
        self._chunks: dict[str, EnrichedChunk] = {}

    async def insert_chunks(self, chunks: list[EnrichedChunk]) -> None:
        for c in chunks:
            self._chunks[c.id] = c

    async def search_vector(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        scored: list[tuple[float, EnrichedChunk]] = []
        for chunk in self._chunks.values():
            if filters and any(chunk.metadata.get(k) != v for k, v in filters.items()):
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
        query_text: str,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        query_tokens = set(query_text.lower().split())
        scored: list[tuple[float, EnrichedChunk]] = []

        for chunk in self._chunks.values():
            if filters and any(chunk.metadata.get(k) != v for k, v in filters.items()):
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
