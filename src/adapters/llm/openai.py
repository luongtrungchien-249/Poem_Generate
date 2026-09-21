import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

from adapters.observability.cost import cost_calculator
from application.ports.llm_client import (
    LLMResponse,
    LLMStreamChunk,
    ToolCallOut,
    ToolSchema,
)
from contracts.chat import Message


def _sang_payload(m: Message) -> dict[str, Any]:
    """Đổi một `Message` sang lượt hội thoại của OpenAI.

    BA VAI CẦN XỬ LÝ RIÊNG, không chỉ role+content:

      - lượt `assistant` XIN GỌI TOOL phải mang `tool_calls`. Bỏ trường này đi thì
        lượt `tool` ngay sau nó trở thành mồ côi và API trả 400.
      - lượt `tool` phải mang `tool_call_id` để ghép với lời gọi tương ứng.
      - `content` của lượt assistant xin gọi tool có thể rỗng — đó là hợp lệ.
    """
    ra: dict[str, Any] = {"role": m.role.value, "content": m.content}
    if m.tool_calls:
        ra["tool_calls"] = m.tool_calls
        # OpenAI đòi content là null (không phải chuỗi rỗng) khi chỉ có tool_calls.
        ra["content"] = m.content or None
    if m.tool_call_id:
        ra["tool_call_id"] = m.tool_call_id
    if m.name:
        ra["name"] = m.name
    return ra


def _sang_tool_openai(t: ToolSchema) -> dict[str, Any]:
    """Lược đồ trung lập -> định dạng function của OpenAI."""
    return {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t.get("description", ""),
            "parameters": t.get("parameters") or {"type": "object", "properties": {}},
        },
    }


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
        tools: list[ToolSchema] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [_sang_payload(m) for m in messages],
            "temperature": temperature,
            **kwargs,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if tools:
            payload["tools"] = [_sang_tool_openai(t) for t in tools]

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]
        tin_nhan = choice["message"]
        # `content` là NULL khi mô hình chỉ xin gọi tool. Bản trước đọc thẳng
        # `choice["message"]["content"]` và gán None vào `LLMResponse.content: str`
        # -> ValidationError ngay lần đầu mô hình gọi tool. Quy về chuỗi rỗng.
        content = tin_nhan.get("content") or ""
        finish_reason = choice.get("finish_reason", "stop")

        tool_calls = [
            ToolCallOut(
                id=tc["id"],
                name=tc["function"]["name"],
                arguments=tc["function"].get("arguments", "") or "",
            )
            for tc in (tin_nhan.get("tool_calls") or [])
            if tc.get("type", "function") == "function"
        ]
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
            tool_calls=tool_calls,
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
            "messages": [_sang_payload(m) for m in messages],
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
