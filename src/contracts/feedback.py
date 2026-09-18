from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    trace_id: str
    rating: Literal[1, -1] # 1: Thumbs up, -1: Thumbs down
    comment: str | None = None
    tags: list[str] = Field(default_factory=list)
    user_id: str | None = "anonymous"
    tenant_id: str | None = "default"


class FeedbackRecord(FeedbackRequest):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
