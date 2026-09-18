from typing import Any

from contracts.chunk import RetrievalResult
from domain.llm.token import TokenManager


class ContextAssembler:
    """Compresses, deduplicates, and structures retrieved chunks into clean LLM context."""

    def __init__(self, max_context_tokens: int = 3000, token_mgr: TokenManager | None = None) -> None:
        self.max_context_tokens = max_context_tokens
        self.token_mgr = token_mgr or TokenManager()

    def assemble(self, results: list[RetrievalResult]) -> tuple[str, list[dict[str, Any]]]:
        if not results:
            return "Không có tài liệu liên quan được tìm thấy.", []

        seen_chunks: set[str] = set()
        context_blocks: list[str] = []
        citations: list[dict[str, Any]] = []
        total_tokens = 0

        for r in results:
            if r.chunk_id in seen_chunks:
                continue
            seen_chunks.add(r.chunk_id)

            block = f"--- [Tài liệu ID: {r.chunk_id}] ---\n{r.content}\n"
            block_tokens = self.token_mgr.count_tokens(block)

            if total_tokens + block_tokens > self.max_context_tokens and context_blocks:
                break

            context_blocks.append(block)
            citations.append({
                "chunk_id": r.chunk_id,
                "doc_id": r.doc_id,
                "score": r.score,
                "title": r.metadata.get("title", ""),
            })
            total_tokens += block_tokens

        return "\n".join(context_blocks), citations
