
from application.ports.llm_client import LLMClient
from contracts.chunk import Chunk, EnrichedChunk


class ChunkEnricher:
    """Enriches raw chunks with embeddings, contextual headers, and summaries."""

    def __init__(self, embedding_client: LLMClient | None = None) -> None:
        self.embedding_client = embedding_client

    async def enrich_chunks(self, chunks: list[Chunk]) -> list[EnrichedChunk]:
        if not chunks:
            return []

        embeddings: list[list[float]] = []
        if self.embedding_client:
            texts = [c.content for c in chunks]
            embeddings = await self.embedding_client.embed(texts)

        enriched: list[EnrichedChunk] = []
        for idx, chunk in enumerate(chunks):
            emb = embeddings[idx] if idx < len(embeddings) else None
            # Contextual prefix: prepends document title to help embedding model
            doc_title = chunk.metadata.get("title", "")
            enriched_content = f"Tài liệu: {doc_title}\n{chunk.content}" if doc_title else chunk.content

            enriched.append(
                EnrichedChunk(
                    id=chunk.id,
                    doc_id=chunk.doc_id,
                    tenant_id=chunk.tenant_id,
                    index=chunk.index,
                    content=enriched_content,
                    token_count=chunk.token_count,
                    metadata=chunk.metadata,
                    embedding=emb,
                )
            )
        return enriched
