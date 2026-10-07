"""Plan_PoeTone GĐ3.4 — vòng ReAct không được để một câu dẫn thế chỗ bài thơ.

Baseline 26/09/2026: 35/160 bài trượt có bản nháp cuối CHỈ MỘT DÒNG. Kịch bản tái
hiện ở đây: mô hình đưa bài vào tham số `kiem_tra_tho`, rồi kết thúc bằng một câu.
"""

from __future__ import annotations

import json

import pytest

from application.pipeline.stages.generate import generate_react_loop
from application.pipeline.stages.verify_output import co_dang_bai_tho
from application.ports.llm import CallContext, LlmReply, LlmUsage, ToolCall, UserMessage
from application.ports.tools import ToolResult, ToolSpec
from application.prompting.context import ContextEnvelope
from domain.common.result import Ok
from domain.conversation.thread import ThreadScope
from tests.fakes.ports import FakeRateLimitPort

pytestmark = pytest.mark.unit

BAI = """Chiều rơi chậm xuống mái rêu xanh
Con ngõ nhỏ dài hơn tiếng ve
Ai đứng bên kia bờ nắng mảnh
Gọi một mùa xa chẳng dám về"""
CTX = CallContext(scope=ThreadScope(platform="web", thread_id="t"), sender_id="u", trace_id="x")
ENV = ContextEnvelope(messages=(UserMessage(content="viết thơ"),), tokens_used=0, has_knowledge=False)
U = LlmUsage(input_tokens=1, output_tokens=1)


class _LlmKichBan:
    """Lượt 1: gọi `kiem_tra_tho` với bài trong tham số. Lượt 2: một câu dẫn."""

    def __init__(self) -> None:
        self.luot = 0

    async def reply(self, messages, tools, ctx, model=None):  # type: ignore[no-untyped-def]
        self.luot += 1
        if self.luot == 1:
            return Ok(LlmReply(text="", usage=U, tool_calls=(
                ToolCall(id="c1", name="kiem_tra_tho", arguments=json.dumps({"van_ban": BAI})),
            )))
        return Ok(LlmReply(text="Bài thơ đã đạt yêu cầu.", tool_calls=(), usage=U))

    async def cheap(self, messages, route, ctx):  # type: ignore[no-untyped-def]
        return Ok("")


class _Tools:
    def specs(self) -> tuple[ToolSpec, ...]:
        return (ToolSpec(name="kiem_tra_tho", description="", parameters={}),)

    async def call_many(self, calls, ctx):  # type: ignore[no-untyped-def]
        return tuple(ToolResult(call_id=c.id, content="đạt") for c in calls)


async def _chay(**kw):  # type: ignore[no-untyped-def]
    return await generate_react_loop(
        envelope=ENV, llm=_LlmKichBan(), tools=_Tools(),  # type: ignore[arg-type]
        rate_limiter=FakeRateLimitPort(), ctx=CTX, **kw,
    )


async def test_duong_tho_lay_lai_bai_tu_tham_so_tool():
    kq = await _chay(la_ban_nhap=co_dang_bai_tho)
    assert isinstance(kq, Ok) and kq.value == BAI


async def test_duong_chat_thuong_giu_nguyen_hanh_vi_cu():
    kq = await _chay()
    assert isinstance(kq, Ok) and kq.value == "Bài thơ đã đạt yêu cầu."


def test_hinh_dang_bai_tho():
    assert co_dang_bai_tho(BAI)
    assert not co_dang_bai_tho("Bài thơ đã đạt yêu cầu.")
    assert not co_dang_bai_tho("Đã hoàn thành các bước suy luận.")
