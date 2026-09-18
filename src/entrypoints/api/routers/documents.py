
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from application.ingest.chunker import TextChunker
from application.ingest.enricher import ChunkEnricher
from application.ingest.loader import DocumentLoader
from entrypoints.api.deps import AppContainer, get_container

router = APIRouter(prefix="/v1/documents", tags=["Documents"])


class DocumentUploadRequest(BaseModel):
    title: str
    content: str
    tenant_id: str | None = "default"
    metadata: dict | None = None


class DocumentUploadResponse(BaseModel):
    document_id: str
    chunks_created: int
    status: str


@router.post("", response_model=DocumentUploadResponse)
async def upload_document(
    req: DocumentUploadRequest,
    app_container: AppContainer = Depends(get_container),
):
    doc = DocumentLoader.from_text(
        text=req.content,
        title=req.title,
        tenant_id=req.tenant_id or "default",
        metadata=req.metadata or {},
    )
    # Save meta
    await app_container.relational_repo.save_document_meta(doc)

    # Ingest: Chunk -> Enrich -> Store
    chunker = TextChunker()
    chunks = chunker.chunk_document(doc)

    enricher = ChunkEnricher(embedding_client=app_container.default_llm)
    enriched_chunks = await enricher.enrich_chunks(chunks)

    await app_container.vector_repo.insert_chunks(enriched_chunks)

    return DocumentUploadResponse(
        document_id=doc.id,
        chunks_created=len(enriched_chunks),
        status="indexed",
    )


@router.get("/{doc_id}/status")
async def get_document_status(
    doc_id: str,
    app_container: AppContainer = Depends(get_container),
):
    doc = await app_container.relational_repo.get_document_meta(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {
        "document_id": doc.id,
        "title": doc.title,
        "status": "indexed",
        "created_at": doc.created_at.isoformat(),
    }
