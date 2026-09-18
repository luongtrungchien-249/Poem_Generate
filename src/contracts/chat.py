from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    role: Role
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


class ChatRequest(BaseModel):
    messages: list[Message]
    stream: bool = False
    model: str | None = "gpt-4o-mini"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, gt=0)
    tier: Literal["cheap", "standard", "reasoning"] | None = "cheap"
    tenant_id: str | None = "default"
    user_id: str | None = "anonymous"
    enable_rag: bool = True
    enable_guardrails: bool = True
    session_id: str | None = None


class StreamDelta(BaseModel):
    delta: str
    finish_reason: str | None = None
    citation_ids: list[str] | None = None
    trace_id: str | None = None


class ChatResponse(BaseModel):
    content: str
    model: str
    finish_reason: str = "stop"
    usage: dict[str, Any] = Field(default_factory=dict)
    cost_usd: float = 0.0
    trace_id: str
    citations: list[dict[str, Any]] = Field(default_factory=list)
    guardrail_verdict: dict[str, Any] | None = None
