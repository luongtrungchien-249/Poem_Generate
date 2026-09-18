import logging

from application.ingest.chunker import TextChunker
from application.ingest.enricher import ChunkEnricher
from bootstrap.container import get_container
from contracts.chunk import Document

logger = logging.getLogger("worker.ingest")


async def run_ingest_task(document: Document) -> int:
    """Worker task: parse → chunk → embed → index."""
    container = get_container()
    logger.info(f"Starting ingestion for document {document.id}: '{document.title}'")

    # 1. Chunking
    chunker = TextChunker()
    raw_chunks = chunker.chunk_document(document)
    logger.info(f"Document {document.id} split into {len(raw_chunks)} chunks.")

    # 2. Enrichment & Batch Embeddings
    enricher = ChunkEnricher(embedding_client=container.default_llm)
    enriched_chunks = await enricher.enrich_chunks(raw_chunks)

    # 3. Vector Indexing
    await container.vector_repo.insert_chunks(enriched_chunks)
    logger.info(f"Successfully indexed {len(enriched_chunks)} chunks for doc {document.id}.")

    return len(enriched_chunks)
