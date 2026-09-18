from typing import Protocol

from contracts.chunk import RetrievalResult


class Reranker(Protocol):
    async def rerank(self, query: str, results: list[RetrievalResult], top_n: int = 5) -> list[RetrievalResult]: ...


class FastHeuristicReranker:
    """Fast lexical and semantic overlap reranker for low-latency production pipelines."""

    async def rerank(self, query: str, results: list[RetrievalResult], top_n: int = 5) -> list[RetrievalResult]:
        if not results:
            return []

        query_terms = set(query.lower().split())
        scored: list[tuple[float, RetrievalResult]] = []

        for item in results:
            content_lower = item.content.lower()
            exact_matches = sum(1 for term in query_terms if term in content_lower)
            density = exact_matches / max(1, len(query_terms))
            # Blend initial retriever score with density score
            blended_score = (item.score * 0.6) + (density * 0.4)
            scored.append((blended_score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        reranked: list[RetrievalResult] = []
        for rank, (score, item) in enumerate(scored[:top_n], start=1):
            reranked.append(
                RetrievalResult(
                    chunk_id=item.chunk_id,
                    doc_id=item.doc_id,
                    content=item.content,
                    score=round(score, 4),
                    rank=rank,
                    source_type=item.source_type,
                    metadata=item.metadata,
                )
            )
        return reranked
