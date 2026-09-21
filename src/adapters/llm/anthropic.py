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


def _sang_tool_anthropic(t: ToolSchema) -> dict[str, Any]:
    """Lược đồ trung lập -> định dạng tool của Anthropic.

    Khác OpenAI đúng ở tên khoá: `parameters` -> `input_schema`, và không bọc
    trong `{"type": "function"}`.
    """
    return {
        "name": t["name"],
        "description": t.get("description", ""),
        "input_schema": t.get("parameters") or {"type": "object", "properties": {}},
    }


def _sang_luot_anthropic(m: Message) -> dict[str, Any]:
    """Đổi một `Message` sang lượt của Anthropic.

    ANTHROPIC KHÁC OPENAI VỀ CƠ BẢN Ở CHỖ NÀY, và đây là chỗ bản trước làm sai:

      - Không có vai `tool`. Kết quả tool là một lượt **user** chứa khối
        `tool_result`, ghép bằng `tool_use_id`.
      - Lời xin gọi tool là một lượt **assistant** chứa khối `tool_use`.

    Bản trước gộp cả `tool` lẫn `user` thành `{"role": "user", "content": <chuỗi>}`,
    tức là ném mất `tool_use_id`. Với API Anthropic, một `tool_use` không có
    `tool_result` tương ứng là lỗi 400; và kể cả khi lọt, mô hình cũng không biết
    kết quả đó thuộc lời gọi nào.
    """
    if m.role.value == "tool":
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": m.tool_call_id or "",
                    "content": m.content,
                }
            ],
        }

    if m.role.value == "assistant" and m.tool_calls:
        khoi: list[dict[str, Any]] = []
        if m.content:
            khoi.append({"type": "text", "text": m.content})
        for tc in m.tool_calls:
            ham = tc.get("function", tc)
            tham_so = ham.get("arguments", "{}")
            try:
                dau_vao = json.loads(tham_so) if isinstance(tham_so, str) else tham_so
            except json.JSONDecodeError:
                # Tham số hỏng thì gửi nguyên văn dưới dạng object một khoá, để mô
                # hình thấy lại đúng thứ nó đã viết thay vì thấy một object rỗng.
                dau_vao = {"_raw": tham_so}
            khoi.append(
                {
                    "type": "tool_use",
                    "id": tc.get("id", ""),
                    "name": ham.get("name", ""),
                    "input": dau_vao,
                }
            )
        return {"role": "assistant", "content": khoi}

    return {
        "role": "user" if m.role.value == "user" else "assistant",
        "content": m.content,
    }


class AnthropicClient:
    """Anthropic Messages API provider."""

    def __init__(self, api_key: str, base_url: str = "https://api.anthropic.com/v1") -> None:
        # Khoá và endpoint do composition root truyền vào; adapter không đọc môi trường.
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    async def generate(
        self,
        messages: list[Message],
        model: str = "claude-3-5-sonnet-20240620",
        temperature: float = 0.7,
        max_tokens: int | None = 4096,
        tools: list[ToolSchema] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        system_msg = next((m.content for m in messages if m.role == "system"), None)
        user_assistant_msgs = [
            _sang_luot_anthropic(m) for m in messages if m.role.value != "system"
        ]

        payload: dict[str, Any] = {
            "model": model,
            "messages": user_assistant_msgs,
            "max_tokens": max_tokens or 4096,
            "temperature": temperature,
            **kwargs,
        }
        if system_msg:
            payload["system"] = system_msg
        if tools:
            payload["tools"] = [_sang_tool_anthropic(t) for t in tools]

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/messages",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        khoi = data.get("content", [])
        content = "".join(c.get("text", "") for c in khoi if c.get("type", "text") == "text")
        tool_calls = [
            ToolCallOut(
                id=c["id"], name=c["name"], arguments=json.dumps(c.get("input", {}), ensure_ascii=False)
            )
            for c in khoi
            if c.get("type") == "tool_use"
        ]
        usage = data.get("usage", {})
        prompt_tokens = usage.get("input_tokens", 0)
        completion_tokens = usage.get("output_tokens", 0)
        cost = cost_calculator.calculate_cost(model, prompt_tokens, completion_tokens)

        return LLMResponse(
            content=content,
            model=model,
            finish_reason=data.get("stop_reason", "end_turn"),
            usage={"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens},
            cost_usd=cost,
            raw_response=data,
            tool_calls=tool_calls,
        )

    async def stream(
        self,
        messages: list[Message],
        model: str = "claude-3-5-sonnet-20240620",
        temperature: float = 0.7,
        max_tokens: int | None = 4096,
        **kwargs: Any,
    ) -> AsyncIterator[LLMStreamChunk]:
        system_msg = next((m.content for m in messages if m.role == "system"), None)
        user_assistant_msgs = [
            {"role": "user" if m.role.value in ["user", "tool"] else "assistant", "content": m.content}
            for m in messages
            if m.role.value != "system"
        ]

        payload: dict[str, Any] = {
            "model": model,
            "messages": user_assistant_msgs,
            "max_tokens": max_tokens or 4096,
            "temperature": temperature,
            "stream": True,
            **kwargs,
        }
        if system_msg:
            payload["system"] = system_msg

        async with httpx.AsyncClient(timeout=60.0) as client, client.stream(
            "POST",
            f"{self.base_url}/messages",
            headers=self._headers(),
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                event_data = line[6:].strip()
                try:
                    parsed = json.loads(event_data)
                    if parsed.get("type") == "content_block_delta":
                        delta = parsed.get("delta", {}).get("text", "")
                        if delta:
                            yield LLMStreamChunk(delta=delta)
                    elif parsed.get("type") == "message_stop":
                        yield LLMStreamChunk(delta="", finish_reason="stop")
                except Exception:
                    continue

    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        # Anthropic doesn't have an embedding API, fallback to mock or downstream
        raise NotImplementedError("Anthropic does not offer embedding endpoints directly. Use OpenAI/vLLM.")
