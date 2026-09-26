"""ReAct ở đường sinh CHÍNH — chủ dự án chốt 22/09/2026.

    *"thay vì trả ra lỗi thì áp dụng ReAct... nếu chưa thoả mãn điều kiện thì
    suy nghĩ rồi mới trả ra kết quả"*

🩸 CHỖ HỎNG ĐƯỢC VÁ. `sinh_theo_kho` gọi thẳng `llm.reply` với `tools=()`. Mô hình
viết MÙ — không đếm được tiếng, không tra được dấu, không có cách nào tự biết mình
vừa viết một dòng 8 tiếng. Hết ứng viên thì khổ bị bỏ và người dùng nhận về lỗi.

Tool `kiem_tra_tho` đã có sẵn và đã đăng ký từ lâu; chỉ là đường này chưa bao giờ
đưa nó cho mô hình.

🔴 BẤT BIẾN KHÔNG ĐƯỢC PHÁ: bước cứu làm bài DỄ ĐẠT HƠN, KHÔNG làm chuẩn đạt THẤP
ĐI. Chủ dự án chốt: hết lượt mà vẫn hỏng thì vẫn chặn.
"""

from __future__ import annotations

import json

import pytest

from application.poetry.requirement import PoetryRequirement, Truong
from application.poetry.sinh_theo_kho import sinh_tung_kho
from application.ports.llm import CallContext, ToolCall, ToolResult
from application.ports.tools import ToolSpec
from domain.common.result import Ok
from domain.conversation.thread import ThreadScope

# 8 tiếng mỗi dòng — đúng kiểu hỏng của bài người dùng mang tới 22/09.
TAM_CHU = "\n".join(
    [
        "Gio heo may len qua tung ke la",
        "Cham vao vai khe cham ca hon tho",
        "Ha Noi thuc trong suong mo bang lang",
        "Thu ve roi thuc hay chi la mo",
    ]
)
BAY_CHU = "\n".join(
    [
        "Chiều rơi chậm xuống mái rêu xanh",
        "Con ngõ nhỏ dài hơn tiếng ve",
        "Ai đứng bên kia bờ nắng mảnh",
        "Gọi một mùa xa chẳng dám về",
    ]
)


def _tra(text: str, tool_calls=()):
    return Ok(type("R", (), {"text": text, "usage": None, "tool_calls": tool_calls})())


class LlmMuRoiSang:
    """Viết bài 8 chữ, và chỉ sửa đúng SAU KHI đã thấy kết quả tool.

    Mô phỏng đúng cơ chế đang vá: mô hình không tự đếm được, nhưng đếm được khi có
    tool. Nếu bước cứu không thật sự đưa tool vào thì test này đỏ.
    """

    def __init__(self) -> None:
        self.da_goi_tool = False
        self.so_luot_co_tool = 0

    async def reply(self, messages, tools, ctx, model=None):
        thay_ket_qua_tool = any(type(m).__name__ == "ToolMessage" for m in messages)
        if tools:
            self.so_luot_co_tool += 1
        if tools and not thay_ket_qua_tool:
            self.da_goi_tool = True
            goi = ToolCall(
                id="1", name="kiem_tra_tho", arguments=json.dumps({"van_ban": TAM_CHU})
            )
            return _tra("", (goi,))
        if thay_ket_qua_tool:
            return _tra(BAY_CHU)
        return _tra(TAM_CHU)


class LlmNgoanCo(LlmMuRoiSang):
    """Trả bài 8 chữ ở MỌI lượt, kể cả sau khi đã soi tool."""

    async def reply(self, messages, tools, ctx, model=None):
        if tools:
            self.so_luot_co_tool += 1
        return _tra(TAM_CHU)


class RL:
    async def within_daily_budget(self, scope):
        return True


class ToolThat:
    """Chạy tool `kiem_tra_tho` THẬT — không giả kết quả kiểm."""

    def specs(self) -> tuple[ToolSpec, ...]:
        from application.agent.tools.registry import tool_registry

        d = tool_registry.get_tool("kiem_tra_tho")
        assert d is not None, "tool chưa đăng ký"
        return (
            ToolSpec(
                name=d.name, description=d.description, parameters=d.parameters_schema
            ),
        )

    async def call_many(self, calls, ctx):
        from application.agent.tools.registry import tool_registry

        ra = []
        for c in calls:
            kq = await tool_registry.execute(c.name, json.loads(c.arguments))
            ra.append(
                ToolResult(
                    call_id=c.id, content=json.dumps(kq, ensure_ascii=False)[:400]
                )
            )
        return tuple(ra)


@pytest.fixture(autouse=True)
def _nap_tool():
    from adapters.tools import register_default_tools

    register_default_tools()


def _req(so_dong: int = 4) -> PoetryRequirement:
    return PoetryRequirement(
        chu_de=Truong(gia_tri="mùa thu", nguon="nguoi_dung"),
        so_dong=Truong(gia_tri=so_dong, nguon="nguoi_dung"),
    )


def _ctx() -> CallContext:
    return CallContext(
        scope=ThreadScope(platform="cli", thread_id="t"), sender_id="u", trace_id="tr"
    )


async def _chay(llm, tools):
    kq = await sinh_tung_kho(
        _req(), llm=llm, ctx=_ctx(), rate_limiter=RL(), so_ung_vien=4, tools=tools
    )
    return kq.value


# ── Chỗ hỏng cũ, và bản vá ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_KHONG_co_tool_thi_bo_cuoc_day_la_hanh_vi_CU():
    """Ghim hành vi trước 22/09 để thấy rõ bản vá đổi cái gì.

    Mô hình viết mù, không cái nào đạt, khổ bị bỏ -> bài rỗng -> người dùng nhận lỗi.
    """
    v = await _chay(LlmMuRoiSang(), None)
    assert v.du_kho is False
    assert v.van_ban == ""


@pytest.mark.asyncio
async def test_CO_tool_thi_SUY_NGHI_roi_moi_tra():
    """Bản vá: hết ứng viên thì tự soi bằng tool, sửa, rồi mới trả."""
    llm = LlmMuRoiSang()
    v = await _chay(llm, ToolThat())
    assert llm.da_goi_tool, "mô hình phải được đưa tool để tự soi"
    assert v.du_kho is True
    assert v.van_ban.splitlines() == BAY_CHU.splitlines()


# ── 🔴 Bất biến: dễ đạt hơn, KHÔNG phải chuẩn thấp đi ───────────────────────


@pytest.mark.asyncio
async def test_van_NGOAN_CO_sai_thi_VAN_CHAN():
    """Chủ dự án chốt 22/09: hết lượt mà vẫn hỏng thì vẫn chặn.

    Bước cứu KHÔNG được nới cổng một ly nào — kết quả ReAct vẫn phải qua
    `kiem_tra_bai_tho` y hệt mọi ứng viên khác.
    """
    llm = LlmNgoanCo()
    v = await _chay(llm, ToolThat())
    assert llm.so_luot_co_tool > 0, "bước cứu phải có chạy"
    assert v.du_kho is False
    assert v.van_ban == "", "bài 8 chữ TUYỆT ĐỐI không được đi ra"


@pytest.mark.asyncio
async def test_buoc_cuu_chi_chay_khi_CAN():
    """Ứng viên đạt ngay thì không tốn một lượt ReAct nào."""

    class LlmTot:
        def __init__(self):
            self.so_luot_co_tool = 0

        async def reply(self, messages, tools, ctx, model=None):
            if tools:
                self.so_luot_co_tool += 1
            return _tra(BAY_CHU)

    llm = LlmTot()
    v = await _chay(llm, ToolThat())
    assert v.du_kho is True
    assert llm.so_luot_co_tool == 0


@pytest.mark.asyncio
async def test_het_ngan_sach_thi_KHONG_chay_buoc_cuu():
    """Bước cứu là một lượt gọi có tính tiền — phải hỏi ngân sách trước."""

    class RLHet:
        def __init__(self):
            self.lan = 0

        async def within_daily_budget(self, scope):
            # Cho khổ đầu chạy, chặn đúng ở bước cứu.
            self.lan += 1
            return self.lan == 1

    llm = LlmMuRoiSang()
    kq = await sinh_tung_kho(
        _req(), llm=llm, ctx=_ctx(), rate_limiter=RLHet(), so_ung_vien=4, tools=ToolThat()
    )
    assert kq.value.du_kho is False
    assert llm.da_goi_tool is False


# ── Chỉ dẫn tự soi ──────────────────────────────────────────────────────────


def test_chi_dan_tu_soi_BAT_BUOC_goi_tool():
    """Tự tin rằng mình đếm đúng chính là kiểu hỏng đang được vá."""
    from application.prompting.system import CHI_DAN_TU_SOI

    assert "Gọi tool" in CHI_DAN_TU_SOI
    assert "ĐỪNG đếm bằng mắt" in CHI_DAN_TU_SOI
    assert "bắt buộc" in CHI_DAN_TU_SOI


def test_chi_dan_tu_soi_KHONG_chep_luat_tho():
    """Nó nói CÁCH LÀM VIỆC (đếm trước khi trả), không nói bài phải thế nào."""
    from application.prompting.system import CHI_DAN_TU_SOI

    for dau_hieu in ("7 tiếng", "bảy tiếng", "B T B", "T B T", "bội của 4"):
        assert dau_hieu not in CHI_DAN_TU_SOI, dau_hieu
