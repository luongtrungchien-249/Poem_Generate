"""Tool `sinh_tho` — nối chat vào máy sinh thơ đã kiểm. 23/09/2026.

Chủ dự án chỉnh định hướng: *"dự án này không phải là giải thích luật thơ mà là
sinh thơ"*. Sổ đăng ký khi đó có `kiem_tra_tho` và `danh_gia_chat_luong_tho` — cả
hai là vai NGƯỜI KIỂM — và không có tool nào SINH thơ.

🔴 BẤT BIẾN: tool này KHÔNG nới cổng. Nó gọi `sinh_bai_tho`, vốn fail-closed.
"""

from __future__ import annotations

import pytest

from adapters.tools.poem_generate import (
    TEN_TOOL,
    _ToolTruBoChinhNo,
    register_poem_generate_tool,
)
from application.agent.tools.registry import tool_registry
from application.ports.tools import ToolSpec

BAI_DAT = (
    "Chiều rơi chậm xuống mái rêu xanh\n"
    "Con ngõ nhỏ dài hơn tiếng ve\n"
    "Ai đứng bên kia bờ nắng mảnh\n"
    "Gọi một mùa xa chẳng dám về"
)


class _ToolGia:
    """Bộ tool có đủ `sinh_tho` — giống hệt bộ mà đường chat cầm."""

    def __init__(self) -> None:
        self.da_goi: list[str] = []

    def specs(self) -> tuple[ToolSpec, ...]:
        return (
            ToolSpec(name=TEN_TOOL, description="sinh tho", parameters={}),
            ToolSpec(name="kiem_tra_tho", description="kiem", parameters={}),
        )

    async def call_many(self, calls, ctx):
        self.da_goi.append("call_many")
        return ()


class _RL:
    async def within_daily_budget(self, scope):
        return True


# ── ⛔ Chặn đệ quy ───────────────────────────────────────────────────────────


def test_bo_tool_dua_xuong_duong_sinh_KHONG_chua_chinh_no():
    """⛔ BẪY LỚN NHẤT của tool này.

    `sinh_bai_tho` truyền `tools` xuống đường lùi, và vòng ReAct ở đó gọi được bất
    cứ tool nào nó thấy. Có `sinh_tho` trong bộ ấy thì mô hình đang SỬA một bài
    thơ có thể gọi lại chính máy sinh thơ — mỗi tầng đệ quy nhân thêm ~36 lượt gọi.
    """
    goc = _ToolGia()
    loc = _ToolTruBoChinhNo(goc)

    assert TEN_TOOL in {s.name for s in goc.specs()}, "bộ gốc phải có, để test có nghĩa"
    assert TEN_TOOL not in {s.name for s in loc.specs()}


def test_loc_KHONG_vut_cac_tool_khac():
    """Lọc quá tay thì bước cứu ReAct mất `kiem_tra_tho` và hết tác dụng."""
    loc = _ToolTruBoChinhNo(_ToolGia())
    assert "kiem_tra_tho" in {s.name for s in loc.specs()}


@pytest.mark.asyncio
async def test_loc_van_chuyen_tiep_call_many():
    """Lọc là một khung nhìn, không phải một bộ tool rỗng."""
    goc = _ToolGia()
    await _ToolTruBoChinhNo(goc).call_many((), None)
    assert goc.da_goi == ["call_many"]


# ── Tool đăng ký được và mô tả đúng việc ────────────────────────────────────


def test_tool_duoc_dang_ky_va_doi_du_tham_so():
    register_poem_generate_tool()
    d = tool_registry.get_tool(TEN_TOOL)
    assert d is not None
    assert set(d.parameters_schema["required"]) == {"chu_de", "so_dong"}


def test_mo_ta_tool_BAO_THANG_dung_tu_viet_tay():
    """Mô tả tool là thứ mô hình đọc để quyết có gọi hay không.

    Không nói rõ thì nó sẽ tự viết — rẻ hơn và nhanh hơn với nó — rồi cho ra bài
    sai luật ở chất lượng p^n.
    """
    register_poem_generate_tool()
    d = tool_registry.get_tool(TEN_TOOL)
    assert "đừng tự viết tay" in d.description.lower()
    assert "ĐÃ QUA BỘ KIỂM" in d.description


# ── Thiếu phụ thuộc thì báo rõ, không im lặng ───────────────────────────────


@pytest.mark.asyncio
async def test_thieu_phu_thuoc_thi_BAO_LOI_khong_im_lang():
    """Im lặng trả rỗng sẽ khiến chat tưởng máy sinh thơ đã chạy và không có bài
    nào đạt — rồi nó tự viết một bài thay thế."""
    register_poem_generate_tool(llm=None, tools=None, rate_limiter=None)
    ra = await tool_registry.execute(TEN_TOOL, {"chu_de": "mùa thu", "so_dong": 4})
    assert "loi" in ra
    assert "ĐỪNG tự viết" in ra["loi"]


# ── Chưa đủ thông tin -> hỏi lại, KHÔNG gọi model ──────────────────────────


@pytest.mark.asyncio
async def test_thieu_chu_de_thi_HOI_LAI_va_khong_ton_luot_goi():
    """Cổng B1 chặn trước khi gọi model — không tốn một đồng.

    Tool phải chuyển nguyên câu hỏi về cho chat, chứ không tự chọn hộ chủ đề.
    """

    class LlmDemLuot:
        def __init__(self):
            self.so_luot = 0

        async def reply(self, **kw):
            self.so_luot += 1
            raise AssertionError("KHÔNG được gọi model khi chưa đủ thông tin")

    llm = LlmDemLuot()
    register_poem_generate_tool(llm=llm, tools=_ToolGia(), rate_limiter=_RL())
    ra = await tool_registry.execute(TEN_TOOL, {"chu_de": "", "so_dong": 4})

    assert ra.get("can_hoi_lai") is True
    assert ra["cau_hoi"]
    assert llm.so_luot == 0
