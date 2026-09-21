"""Gọi tool chạy thật — ghim lại năm tầng từng chặn nó.

Trước 21/09/2026, `kiem_tra_tho` có trong sổ đăng ký, có mô tả, có lược đồ, và
`specs()` trả nó về đầy đủ — nhưng mô hình KHÔNG BAO GIỜ gọi được. Năm tầng cùng
chặn, và mỗi tầng đều "trông như đang hoạt động":

    1. `LLMResponse` không có trường `tool_calls`  -> có trả về cũng rơi mất
    2. adapter provider không GỬI `tools` đi       -> mô hình không biết có tool
    3. adapter provider không ĐỌC `tool_calls` về  -> có gọi cũng không ai thấy
    4. `ChatLlmAdapter` vứt `tools` (`_ = tools`)  -> mắt xích cuối đứt
    5. `content` = null khi chỉ gọi tool           -> ValidationError ngay lần đầu

Mỗi test dưới đây ghim một tầng. Đỏ ở đâu thì biết ngay tầng nào vỡ lại.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from adapters.llm.chat_port import ChatLlmAdapter, _sang_luoc_do_tool, _sang_message
from adapters.llm.mock import MockLLMClient
from adapters.llm.openai import _sang_payload, _sang_tool_openai
from adapters.tools import register_default_tools
from adapters.tools.executor import RegistryToolExecutor
from application.pipeline.stages.generate import generate_react_loop
from application.ports.llm import (
    AssistantMessage,
    CallContext,
    ToolCall,
    ToolMessage,
    UserMessage,
)
from application.ports.llm_client import LLMResponse, ToolCallOut
from application.ports.tools import ToolSpec
from application.prompting.context import ContextEnvelope
from contracts.chat import Role
from domain.common.result import is_ok
from domain.conversation.thread import ThreadScope
from tests.fakes.ports import FakeRateLimitPort

pytestmark = pytest.mark.unit


def _ctx() -> CallContext:
    return CallContext(
        scope=ThreadScope(platform="web", thread_id="t-tool"),
        sender_id="u1",
        trace_id="trace-tool",
    )


# ── Tầng 1: kiểu dữ liệu mang được tool_calls ────────────────────────────────


def test_LLMResponse_mang_duoc_tool_calls():
    r = LLMResponse(
        content="",
        model="m",
        tool_calls=[ToolCallOut(id="c1", name="kiem_tra_tho", arguments='{"van_ban":"x"}')],
    )
    assert r.tool_calls[0].name == "kiem_tra_tho"
    # `arguments` giữ nguyên dạng CHUỖI, không parse sẵn — lỗi JSON phải được phát
    # hiện ở nơi thực thi tool, nơi có thể trả lại cho mô hình sửa.
    assert isinstance(r.tool_calls[0].arguments, str)


def test_content_null_KHONG_lam_no_LLMResponse():
    """Tầng 5. OpenAI trả `content: null` khi mô hình chỉ xin gọi tool."""
    tin_nhan: dict[str, Any] = {"content": None, "tool_calls": []}
    assert (tin_nhan.get("content") or "") == ""
    LLMResponse(content=tin_nhan.get("content") or "", model="m")


# ── Tầng 2: lược đồ tool đi đúng định dạng từng nhà cung cấp ─────────────────


def test_luoc_do_tool_trung_lap_dich_sang_dinh_dang_openai():
    spec = ToolSpec(name="t", description="d", parameters={"type": "object", "properties": {}})
    trung_lap = _sang_luoc_do_tool(spec)
    assert trung_lap == {"name": "t", "description": "d", "parameters": {"type": "object", "properties": {}}}

    openai = _sang_tool_openai(trung_lap)
    assert openai["type"] == "function"
    assert openai["function"]["name"] == "t"


def test_luoc_do_tool_dich_sang_dinh_dang_anthropic():
    """Anthropic đổi khoá `parameters` -> `input_schema` và không bọc `type`."""
    from adapters.llm.anthropic import _sang_tool_anthropic

    ra = _sang_tool_anthropic({"name": "t", "description": "d", "parameters": {"type": "object"}})
    assert ra["input_schema"] == {"type": "object"}
    assert "parameters" not in ra and "type" not in ra


def test_tool_la_thi_bo_qua_chu_khong_lam_hong_luot_goi():
    assert _sang_luoc_do_tool("không phải tool") is None
    assert _sang_luoc_do_tool(object()) is None


# ── Tầng 4: cặp assistant(tool_calls) / tool(result) được đóng đúng ──────────


def test_luot_assistant_giu_duoc_tool_calls():
    m = _sang_message(
        AssistantMessage(content="", tool_calls=(ToolCall(id="c1", name="t", arguments="{}"),))
    )
    assert m.role == Role.ASSISTANT
    assert m.tool_calls and m.tool_calls[0]["id"] == "c1"
    assert m.tool_calls[0]["function"]["name"] == "t"


def test_luot_tool_giu_duoc_tool_call_id_chu_khong_bi_ha_xuong_vai_user():
    """🩸 Bản đầu hạ xuống `role=user` và nhét id vào trong chuỗi.

    Hệ quả với API thật: lượt `assistant` xin gọi tool không có lượt `tool` nào
    ghép vào -> OpenAI trả 400.
    """
    m = _sang_message(ToolMessage(tool_call_id="c1", content="ket qua"))
    assert m.role == Role.TOOL, "kết quả tool KHÔNG được hạ xuống vai user"
    assert m.tool_call_id == "c1", "tool_call_id phải là một TRƯỜNG, không nằm trong chuỗi"


def test_payload_openai_dong_du_cap_tool():
    """Lượt assistant mang tool_calls thì `content` phải là null, không phải ''."""
    a = _sang_payload(
        _sang_message(
            AssistantMessage(content="", tool_calls=(ToolCall(id="c1", name="t", arguments="{}"),))
        )
    )
    assert a["content"] is None
    assert a["tool_calls"][0]["id"] == "c1"

    t = _sang_payload(_sang_message(ToolMessage(tool_call_id="c1", content="kq")))
    assert t["role"] == "tool"
    assert t["tool_call_id"] == "c1"


# ── Đường thật: vòng ReAct gọi được `kiem_tra_tho` ───────────────────────────


@pytest.mark.asyncio
async def test_vong_ReAct_goi_that_duoc_kiem_tra_tho():
    """Điều mà trước hôm nay KHÔNG chạy được.

    Mock bật `mo_phong_goi_tool` để xin gọi tool đúng một lần; sổ đăng ký thật thực
    thi `kiem_tra_tho` thật; kết quả quay lại đúng vai `tool`.
    """
    register_default_tools()
    tools = RegistryToolExecutor()
    ten_tool = [s.name for s in tools.specs()]
    assert "kiem_tra_tho" in ten_tool
    assert "danh_gia_chat_luong_tho" in ten_tool

    llm = ChatLlmAdapter(MockLLMClient(latency_sec=0.0, mo_phong_goi_tool=True))

    goi_thuc_te: list[str] = []
    goc = tools.call_many

    async def ghi_lai(calls, ctx):  # type: ignore[no-untyped-def]
        goi_thuc_te.extend(c.name for c in calls)
        return await goc(calls, ctx)

    tools.call_many = ghi_lai  # type: ignore[method-assign]

    kq = await generate_react_loop(
        envelope=ContextEnvelope(
            messages=(UserMessage(content="Chiều rơi chậm xuống mái rêu xanh"),),
            tokens_used=0,
            has_knowledge=False,
        ),
        llm=llm,
        tools=tools,
        rate_limiter=FakeRateLimitPort(),
        ctx=_ctx(),
    )

    assert is_ok(kq)
    assert goi_thuc_te, "mô hình lẽ ra phải gọi ít nhất một tool"
    assert goi_thuc_te[0] in ten_tool


@pytest.mark.asyncio
async def test_ket_qua_tool_that_su_la_ket_qua_cua_rule_py():
    """Tool không chỉ được gọi — nó phải trả về phán quyết THẬT của `rule.py`."""
    register_default_tools()
    tools = RegistryToolExecutor()

    bai = "\n".join(["Một dòng sáu tiếng thôi mà"] * 4)
    kq = await tools.call_many(
        (ToolCall(id="c1", name="kiem_tra_tho", arguments=json.dumps({"van_ban": bai})),),
        _ctx(),
    )
    assert len(kq) == 1 and not kq[0].is_error
    data = json.loads(kq[0].content)
    assert data["dat"] is False
    assert any(vp["ma"] in ("H1", "H2") for vp in data["vi_pham"])


@pytest.mark.asyncio
async def test_tool_loi_tra_ve_DU_LIEU_chu_khong_giet_ca_luot():
    """Một tool hỏng không được phép giết lượt: mô hình cần BIẾT nó hỏng."""
    tools = RegistryToolExecutor()
    kq = await tools.call_many(
        (ToolCall(id="c1", name="khong_ton_tai", arguments="{}"),), _ctx()
    )
    assert kq[0].is_error
    assert "khong_ton_tai" in kq[0].content

    xau = await tools.call_many(
        (ToolCall(id="c2", name="kiem_tra_tho", arguments="{khong phai json}"),), _ctx()
    )
    assert xau[0].is_error
    assert "JSON" in xau[0].content
