import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

from adapters.observability.cost import cost_calculator
from application.ports.llm_client import LLMResponse, LLMStreamChunk
from contracts.chat import Message


class OpenAIClient:
    """OpenAI API client supporting both standard and streaming chat completions and embeddings."""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1") -> None:
        # Khoá và endpoint do composition root truyền vào; adapter không đọc môi trường.
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate(
        self,
        messages: list[Message],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [{"role": m.role.value, "content": m.content} for m in messages],
            "temperature": temperature,
            **kwargs,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]
        content = choice["message"]["content"]
        finish_reason = choice.get("finish_reason", "stop")
        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        cost = cost_calculator.calculate_cost(model, prompt_tokens, completion_tokens)
        return LLMResponse(
            content=content,
            model=model,
            finish_reason=finish_reason,
            usage=usage,
            cost_usd=cost,
            raw_response=data,
        )

    async def stream(
        self,
        messages: list[Message],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[LLMStreamChunk]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [{"role": m.role.value, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": True,
            **kwargs,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client, client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                line_data = line[6:].strip()
                if line_data == "[DONE]":
                    break
                try:
                    chunk_json = json.loads(line_data)
                    delta = chunk_json["choices"][0].get("delta", {}).get("content", "")
                    finish_reason = chunk_json["choices"][0].get("finish_reason")
                    if delta or finish_reason:
                        yield LLMStreamChunk(delta=delta, finish_reason=finish_reason)
                except Exception:
                    continue

    async def embed(
        self,
        texts: list[str],
        model: str | None = "text-embedding-3-small",
    ) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/embeddings",
                headers=self._headers(),
                json={"input": texts, "model": model},
            )
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]
