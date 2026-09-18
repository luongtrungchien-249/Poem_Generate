import pytest

from adapters.llm.mock import MockLLMClient
from adapters.persistence.memory.vector import InMemoryVectorRepository
from application.ingest.chunker import TextChunker
from application.ingest.enricher import ChunkEnricher
from application.ingest.loader import DocumentLoader
from application.rag.context_builder import ContextAssembler
from application.rag.retriever import HybridRetriever


@pytest.mark.asyncio
async def test_rag_pipeline_end_to_end():
    mock_llm = MockLLMClient()
    vector_repo = InMemoryVectorRepository()

    # 1. Load document
    content = "Hệ thống AI Production yêu cầu kiểm thử tự động CI/CD. Đảm bảo độ sẵn sàng 99.9%."
    doc = DocumentLoader.from_text(text=content, title="Production AI Guide", tenant_id="acme")
    assert doc.title == "Production AI Guide"

    # 2. Chunking
    chunker = TextChunker(chunk_size_tokens=100, chunk_overlap_tokens=10)
    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 1

    # 3. Enrich & Index
    enricher = ChunkEnricher(embedding_client=mock_llm)
    enriched = await enricher.enrich_chunks(chunks)
    assert enriched[0].embedding is not None
    await vector_repo.insert_chunks(enriched)

    # 4. Retrieve
    retriever = HybridRetriever(vector_repo=vector_repo, llm_client=mock_llm)
    results = await retriever.retrieve(query="kiểm thử tự động", top_k=2)
    assert len(results) >= 1

    # 5. Context Assembly
    assembler = ContextAssembler()
    context_text, citations = assembler.assemble(results)
    assert "kiểm thử tự động" in context_text
    assert len(citations) >= 1
