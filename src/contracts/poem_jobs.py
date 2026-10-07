from typing import Any, Literal

from pydantic import BaseModel, Field

from .poem import CanLamRo, PoemKhongDat, PoemResponse


class PoemJobResponse(BaseModel):
    job_id: str
    status: Literal[
        "queued",
        "planning",
        "generating",
        "verifying",
        "repairing",
        "completed",
        "failed",
        "cancelled",
        "expired",
    ]
    conversation_id: str | None = None
    created_at: float
    updated_at: float
    deadline: float
    model: str
    provider: str
    progress: dict[str, Any] = Field(default_factory=dict)
    result: PoemResponse | CanLamRo | PoemKhongDat | None = None
    result_status: int | None = None
    error: str | None = None
