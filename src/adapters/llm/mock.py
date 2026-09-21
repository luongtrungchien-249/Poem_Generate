import asyncio
import hashlib
import json
from collections.abc import AsyncIterator
from typing import Any

from adapters.observability.cost import cost_calculator
from application.ports.llm_client import (
    LLMResponse,
    LLMStreamChunk,
    ToolCallOut,
    ToolSchema,
)
from contracts.chat import Message


def _tham_so_mau(t: ToolSchema, van_ban: str) -> dict[str, Any]:
    """Điền tham số bắt buộc của tool bằng giá trị đọc được.

    Điền theo LƯỢC ĐỒ chứ không đoán tên trường: tool nào cũng khai `required` và
    kiểu, nên suy ra được một giá trị hợp lệ mà không cần biết tool đó là tool gì.
    """
    schema = t.get("parameters") or {}
    props: dict[str, Any] = schema.get("properties", {})
    ra: dict[str, Any] = {}
    for ten in schema.get("required", []):
        kieu = props.get(ten, {}).get("type", "string")
        ra[ten] = {"string": van_ban, "integer": 1, "number": 1.0, "boolean": True}.get(kieu, van_ban)
    return ra


class MockLLMClient:
    """Mock LLM provider for unit tests, offline evaluation, and local development.

    MOCK NÀY CỐ Ý KHÔNG SINH THƠ. Nó trả một câu mô tả, nên mọi yêu cầu thơ đi qua
    nó đều bị cổng kiểm định chặn và trả 422. Đó là hành vi ĐÚNG và có ích: nó ép
    test đi vào đúng nhánh đáng lo nhất — mô hình trả rác ở mọi lượt — thay vì cho
    một cảm giác an toàn giả.

    MÔ PHỎNG GỌI TOOL (`mo_phong_goi_tool=True`). Khi bật, mock xin gọi tool đầu
    tiên trong danh sách đúng MỘT lần rồi mới trả lời. Dùng để kiểm chứng vòng
    ReAct chạy thật — có đóng đủ cặp `assistant(tool_calls)` / `tool(result)` —
    mà không cần khoá API. Mặc định TẮT để không làm nhiễu các test khác.
    """

    def __init__(self, latency_sec: float = 0.05, *, mo_phong_goi_tool: bool = False) -> None:
        self.latency_sec = latency_sec
        self.mo_phong_goi_tool = mo_phong_goi_tool

    async def generate(
        self,
        messages: list[Message],
        model: str = "mock-gpt",
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[ToolSchema] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        await asyncio.sleep(self.latency_sec)
        user_msg = next((m.content for m in reversed(messages) if m.role == "user"), "Hello!")

        # Đã có kết quả tool trong lịch sử -> lượt này trả lời thẳng, không xin nữa.
        # Thiếu điều kiện này thì mock xin gọi tool ở mọi lượt và vòng ReAct chạy
        # tới trần lặp — một vòng lặp vô hạn trá hình.
        da_goi_tool = any(m.role.value == "tool" for m in messages)
        if self.mo_phong_goi_tool and tools and not da_goi_tool:
            t = tools[0]
            return LLMResponse(
                content="",
                model=model,
                finish_reason="tool_calls",
                usage={"prompt_tokens": 0, "completion_tokens": 0},
                tool_calls=[
                    ToolCallOut(
                        id="mock-call-1",
                        name=t["name"],
                        arguments=json.dumps(
                            _tham_so_mau(t, user_msg), ensure_ascii=False
                        ),
                    )
                ],
            )

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
