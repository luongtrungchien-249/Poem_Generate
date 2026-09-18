from contracts.chunk import Chunk, Document
from domain.llm.token import TokenManager


class TextChunker:
    """Chunks documents into token-bounded chunks with sliding overlap."""

    def __init__(self, chunk_size_tokens: int = 500, chunk_overlap_tokens: int = 50) -> None:
        self.chunk_size = chunk_size_tokens
        self.chunk_overlap = chunk_overlap_tokens
        self.token_mgr = TokenManager()

    def chunk_document(self, doc: Document) -> list[Chunk]:
        words = doc.content.split()
        if not words:
            return []

        chunks: list[Chunk] = []
        start_idx = 0
        chunk_index = 0

        # Approximate words per token ~0.75
        words_per_chunk = int(self.chunk_size * 0.75)
        overlap_words = int(self.chunk_overlap * 0.75)

        while start_idx < len(words):
            end_idx = min(len(words), start_idx + words_per_chunk)
            chunk_words = words[start_idx:end_idx]
            content = " ".join(chunk_words)
            token_count = self.token_mgr.count_tokens(content)

            chunk = Chunk(
                id=f"{doc.id}_chunk_{chunk_index}",
                doc_id=doc.id,
                tenant_id=doc.tenant_id,
                index=chunk_index,
                content=content,
                token_count=token_count,
                metadata={
                    **doc.metadata,
                    "title": doc.title,
                    "chunk_index": chunk_index,
                },
            )
            chunks.append(chunk)
            chunk_index += 1

            if end_idx == len(words):
                break
            start_idx = end_idx - overlap_words

        return chunks
