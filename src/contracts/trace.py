from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SpanEvent(BaseModel):
    name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    attributes: dict[str, Any] = Field(default_factory=dict)
    duration_ms: float | None = None


class TraceContext(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    request_id: str
    tenant_id: str = "default"
    user_id: str = "anonymous"
    spans: list[SpanEvent] = Field(default_factory=list)
    total_tokens: int = 0
    total_cost_usd: float = 0.0
