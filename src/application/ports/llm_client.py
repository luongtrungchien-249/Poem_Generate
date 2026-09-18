from collections.abc import AsyncIterator
from typing import Any, Protocol

from pydantic import BaseModel, Field

from contracts.chat import Message


class LLMResponse(BaseModel):
    content: str
    model: str
    finish_reason: str = "stop"
    usage: dict[str, Any] = Field(default_factory=dict)
    cost_usd: float = 0.0
    raw_response: dict[str, Any] | None = None


class LLMStreamChunk(BaseModel):
    delta: str
    finish_reason: str | None = None
    usage: dict[str, Any] | None = None


class LLMClient(Protocol):
    """Unified interface for all LLM providers."""

    async def generate(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> LLMResponse: ...

    # KHÔNG phải `async def`: mọi hiện thực đều là async generator, nên gọi hàm
    # này trả thẳng AsyncIterator chứ không trả coroutine. Khai `async def` ở đây
    # nghĩa là "coroutine trả về AsyncIterator", buộc nơi gọi phải `await` trước
    # khi lặp — trái với cách adapter thật hoạt động.
    def stream(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[LLMStreamChunk]: ...

    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> list[list[float]]: ...
