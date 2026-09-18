import asyncio
import hashlib
from collections.abc import AsyncIterator
from typing import Any

from adapters.observability.cost import cost_calculator
from application.ports.llm_client import LLMResponse, LLMStreamChunk
from contracts.chat import Message


class MockLLMClient:
    """Mock LLM provider for unit tests, offline evaluation, and local development."""

    def __init__(self, latency_sec: float = 0.05) -> None:
        self.latency_sec = latency_sec

    async def generate(
        self,
        messages: list[Message],
        model: str = "mock-gpt",
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        await asyncio.sleep(self.latency_sec)
        user_msg = next((m.content for m in reversed(messages) if m.role == "user"), "Hello!")
        
        reply_content = f"[AI Production Response] Answered query: '{user_msg}' using model {model}."
        prompt_tokens = sum(len(m.content.split()) * 2 for m in messages)
        completion_tokens = len(reply_content.split()) * 2

        cost = cost_calculator.calculate_cost(model, prompt_tokens, completion_tokens)
        return LLMResponse(
            content=reply_content,
            model=model,
            finish_reason="stop",
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            cost_usd=cost,
        )

    async def stream(
        self,
        messages: list[Message],
        model: str = "mock-gpt",
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[LLMStreamChunk]:
        user_msg = next((m.content for m in reversed(messages) if m.role == "user"), "Hello!")
        words = f"[Streaming Mock] Processed request: '{user_msg}'.".split()

        for word in words:
            await asyncio.sleep(self.latency_sec)
            yield LLMStreamChunk(delta=word + " ")
        yield LLMStreamChunk(delta="", finish_reason="stop")

    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> list[list[float]]:
        # Generate deterministic 64-dim embedding vector based on sha256 hash
        results: list[list[float]] = []
        for text in texts:
            h = hashlib.sha256(text.encode("utf-8")).digest()
            vec = [(float(b) / 128.0) - 1.0 for b in h[:64]]
            results.append(vec)
        return results
