from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str
    tenant_id: str = "default"
    title: str
    content: str
    mime_type: str = "text/plain"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Chunk(BaseModel):
    id: str
    doc_id: str
    tenant_id: str = "default"
    index: int
    content: str
    token_count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class EnrichedChunk(Chunk):
    embedding: list[float] | None = None
    summary: str | None = None
    entities: list[str] = Field(default_factory=list)


class RetrievalResult(BaseModel):
    chunk_id: str
    doc_id: str
    content: str
    score: float
    rank: int
    source_type: str # "dense", "sparse", "hybrid"
    metadata: dict[str, Any] = Field(default_factory=dict)
