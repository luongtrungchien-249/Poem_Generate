"""Adapter Google AI — phần THUẦN, test được không cần mạng.

Gemini API khác OpenAI ở năm chỗ, và mỗi chỗ là một cơ hội dịch sai lặng lẽ. Test
ở đây ghim từng phép dịch một, vì một lỗi dịch sẽ biểu hiện thành "mô hình trả lời
kém" chứ không thành lỗi 500 — kiểu hỏng khó truy nhất.
"""

from __future__ import annotations

import json

import pytest

from adapters.llm.google import (
    MODEL_NHUNG_MAC_DINH,
    GoogleAIClient,
    _doc_phan_hoi,
    _duong_dan_model,
    _sang_luot_google,
    _sang_tool_google,
)
from contracts.chat import Message, Role


def _client() -> GoogleAIClient:
    return GoogleAIClient(api_key="khoa-thu")


# ── Tên model ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("vao", "ra"),
    [
        ("gemma-3-27b-it", "models/gemma-3-27b-it"),
        ("gemini-2.0-flash", "models/gemini-2.0-flash"),
        ("models/gemini-2.0-flash", "models/gemini-2.0-flash"),
    ],
)
def test_ten_model_duoc_chuan_hoa(vao, ra):
    """Truyền tên trần lên đường dẫn Gemini API là 404 — phải có tiền tố."""
    assert _duong_dan_model(vao) == ra


# ── Dịch lượt hội thoại ─────────────────────────────────────────────────────


def test_assistant_thanh_model():
    """Google gọi vai assistant là `model`. Gửi "assistant" là 400."""
    ra = _sang_luot_google(Message(role=Role.ASSISTANT, content="chào"))
    assert ra["role"] == "model"
    assert ra["parts"] == [{"text": "chào"}]


def test_user_giu_nguyen_va_boc_parts():
    ra = _sang_luot_google(Message(role=Role.USER, content="viết thơ"))
    assert ra == {"role": "user", "parts": [{"text": "viết thơ"}]}


def test_ket_qua_tool_thanh_luot_USER_co_functionResponse():
    """⛔ Google KHÔNG có vai `tool`. Kết quả tool là một lượt user."""
    ra = _sang_luot_google(
        Message(role=Role.TOOL, content='{"so_dong": 4}', name="kiem_tra_tho")
    )
    assert ra["role"] == "user"
    fr = ra["parts"][0]["functionResponse"]
    assert fr["name"] == "kiem_tra_tho"
    assert fr["response"] == {"so_dong": 4}


def test_ket_qua_tool_KHONG_phai_json_van_duoc_boc():
    """`response` bắt buộc là object — chuỗi trần sẽ bị API từ chối."""
    ra = _sang_luot_google(Message(role=Role.TOOL, content="hỏng rồi", name="t"))
    assert ra["parts"][0]["functionResponse"]["response"] == {"ket_qua": "hỏng rồi"}


def test_loi_goi_tool_thanh_luot_model_co_functionCall():
    ra = _sang_luot_google(
        Message(
            role=Role.ASSISTANT,
            content="",
            tool_calls=[
                {
                    "id": "1",
                    "function": {"name": "kiem_tra_tho", "arguments": '{"van_ban": "x"}'},
                }
            ],
        )
    )
    assert ra["role"] == "model"
    fc = ra["parts"][0]["functionCall"]
    assert fc["name"] == "kiem_tra_tho"
    assert fc["args"] == {"van_ban": "x"}


def test_tham_so_tool_HONG_thi_giu_nguyen_van():
    """Gửi object rỗng là xoá dấu vết — mô hình phải thấy lại thứ nó đã viết."""
    ra = _sang_luot_google(
        Message(
            role=Role.ASSISTANT,
            content="",
            tool_calls=[{"id": "1", "function": {"name": "t", "arguments": "{khong-phai-json"}}],
        )
    )
    assert ra["parts"][0]["functionCall"]["args"] == {"_raw": "{khong-phai-json"}


# ── Lược đồ tool ────────────────────────────────────────────────────────────


def test_tool_KHONG_boc_trong_type_function():
    """Khác OpenAI: Google nhận ba khoá trần, không có lớp `{"type":"function"}`."""
    ra = _sang_tool_google(
        {"name": "kiem_tra_tho", "description": "kiểm", "parameters": {"type": "object"}}
    )
    assert set(ra) == {"name", "description", "parameters"}
    assert "type" not in ra


def test_tool_thieu_parameters_van_hop_le():
    ra = _sang_tool_google({"name": "ping"})
    assert ra["parameters"] == {"type": "object", "properties": {}}


# ── Dựng payload ────────────────────────────────────────────────────────────


def test_system_tach_ra_systemInstruction_KHONG_nam_trong_contents():
    """⛔ Đây là chỗ dễ sai nhất.

    Để lượt system trong `contents` thì Google đọc nó như một lượt user bình
    thường — chỉ dẫn hệ thống tụt xuống ngang hàng dữ liệu, và không ai thấy.
    """
    than = _client()._than_yeu_cau(
        [
            Message(role=Role.SYSTEM, content="bạn là trợ lý thơ"),
            Message(role=Role.USER, content="viết đi"),
        ],
        temperature=0.7,
        max_tokens=None,
        tools=None,
        them={},
    )
    assert than["systemInstruction"] == {"parts": [{"text": "bạn là trợ lý thơ"}]}
    assert len(than["contents"]) == 1
    assert than["contents"][0]["role"] == "user"


def test_tools_gom_vao_MOT_phan_tu():
    """Google gom mọi tool dưới một `functionDeclarations`, khác OpenAI."""
    than = _client()._than_yeu_cau(
        [Message(role=Role.USER, content="x")],
        temperature=0.5,
        max_tokens=100,
        tools=[{"name": "a"}, {"name": "b"}],
        them={},
    )
    assert len(than["tools"]) == 1
    assert [t["name"] for t in than["tools"][0]["functionDeclarations"]] == ["a", "b"]


def test_temperature_va_maxOutputTokens_nam_trong_generationConfig():
    """Đặt thẳng ở gốc payload như OpenAI thì Google bỏ qua — im lặng."""
    than = _client()._than_yeu_cau(
        [Message(role=Role.USER, content="x")], 0.3, 256, None, {}
    )
    assert than["generationConfig"] == {"temperature": 0.3, "maxOutputTokens": 256}
    assert "temperature" not in than


def test_khong_co_tool_thi_KHONG_gui_truong_tools():
    """Gửi `tools: []` cho model không hỗ trợ là 400 không cần thiết."""
    than = _client()._than_yeu_cau([Message(role=Role.USER, content="x")], 0.7, None, None, {})
    assert "tools" not in than


# ── Đọc phản hồi ────────────────────────────────────────────────────────────


def test_doc_van_ban_tu_candidates():
    kq = _doc_phan_hoi(
        {
            "candidates": [{"content": {"parts": [{"text": "Chiều rơi"}, {"text": " chậm"}]},
                            "finishReason": "STOP"}],
            "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5},
        },
        "gemma-3-27b-it",
    )
    assert kq.content == "Chiều rơi chậm"
    assert kq.usage == {"prompt_tokens": 10, "completion_tokens": 5}


def test_doc_loi_goi_tool_va_TU_DUNG_ID():
    """Google KHÔNG cấp id cho lời gọi tool, nhưng `ToolCallOut.id` bắt buộc —
    và vòng ReAct dùng id để ghép kết quả."""
    kq = _doc_phan_hoi(
        {"candidates": [{"content": {"parts": [
            {"functionCall": {"name": "kiem_tra_tho", "args": {"van_ban": "x"}}}
        ]}}]},
        "gemini-2.0-flash",
    )
    assert len(kq.tool_calls) == 1
    tc = kq.tool_calls[0]
    assert tc.name == "kiem_tra_tho"
    assert tc.id, "id rỗng thì vòng ReAct không ghép được kết quả"
    assert json.loads(tc.arguments) == {"van_ban": "x"}


def test_phan_hoi_RONG_khong_no():
    """Model bị chặn nội dung trả về `candidates` rỗng — không được ném."""
    kq = _doc_phan_hoi({}, "gemma-3-27b-it")
    assert kq.content == ""
    assert kq.tool_calls == []


# ── Nối dây composition root ────────────────────────────────────────────────


def test_provider_google_duoc_nhan_trong_cau_hinh():
    from bootstrap.settings import PROVIDER_HOP_LE

    assert "google" in PROVIDER_HOP_LE


def test_container_dung_duoc_GoogleAIClient():
    """Khai trong Literal mà composition root không dựng được là một nhánh chết."""
    import inspect

    from bootstrap import container

    nguon = inspect.getsource(container._build_llm)
    assert 'provider == "google"' in nguon
    assert "GoogleAIClient" in nguon
    assert "google_api_key" in nguon


def test_model_nhung_KHAC_model_sinh():
    """Dùng model sinh cho `:batchEmbedContents` là 400 với thông báo mơ hồ."""
    assert "embedding" in MODEL_NHUNG_MAC_DINH
