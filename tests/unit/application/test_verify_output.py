"""Chứng minh cổng kiểm định không rò.

Điều phải chứng minh không phải "vòng sửa hoạt động", mà là điều mạnh hơn:
KHÔNG CÓ ĐƯỜNG NÀO để một bài sai luật đi ra ngoài, kể cả khi mô hình ngoan cố
trả sai ở mọi lượt.

Fake viết tay, không mock framework: Protocol khớp cấu trúc nên một fake chỉ cần
đủ phương thức. Vá vào nội bộ sẽ cho test xanh trong khi đường thật đã đổi.
"""

from typing import Any

import pytest

from application.pipeline.stages.verify_output import (
    THANG_LEO_THANG,
    generate_with_verification,
)
from application.poem_verifier import MA_THE, PoemVerifier
from application.ports.llm import CallContext, LlmMessage, LlmReply, LlmUsage
from application.ports.verifier import OutputSpec
from application.prompting.context import ContextEnvelope
from application.prompting.instructions import CHI_DAN_SUA
from domain.common.errors import BotError, OutputKhongDat, is_retryable
from domain.common.result import Ok, Result, is_err, is_ok
from domain.conversation.thread import ThreadScope
from tests.fakes.ports import FakeRateLimitPort, FakeToolPort

BAI_DAT = """Chiều rơi chậm xuống mái rêu xanh
Con ngõ nhỏ dài hơn tiếng ve
Ai đứng bên kia bờ nắng mảnh
Gọi một mùa xa chẳng dám về"""

BAI_SAI = """Chiều rơi chậm xuống mái rêu xanh xa
Con ngõ nhỏ dài hơn tiếng ve
Ai đứng bên kia
Gọi một mùa xa chẳng dám về"""

BAI_SAI_KHAC = """Chiều rơi chậm xuống mái rêu xanh biếc
Con ngõ nhỏ dài hơn tiếng ve
Ai đứng bên kia bờ
Gọi một mùa xa chẳng dám về"""


class LlmTheoKichBan:
    """Trả lần lượt các bản nháp đã định sẵn; hết kịch bản thì lặp lại bản cuối."""

    def __init__(self, *ban_nhap: str) -> None:
        self.kich_ban = list(ban_nhap)
        self.so_lan_goi = 0
        self.luot_nhan: list[tuple[LlmMessage, ...]] = []

    async def reply(
        self,
        messages: tuple[LlmMessage, ...],
        tools: tuple[Any, ...],
        ctx: CallContext,
        model: str | None = None,
    ) -> Result[LlmReply, BotError]:
        self.luot_nhan.append(messages)
        i = min(self.so_lan_goi, len(self.kich_ban) - 1)
        self.so_lan_goi += 1
        return Ok(
            LlmReply(
                text=self.kich_ban[i],
                tool_calls=(),
                usage=LlmUsage(input_tokens=10, output_tokens=10),
            )
        )

    async def cheap(self, messages: Any, route: Any, ctx: Any) -> Result[str, BotError]:
        return Ok("fake")


class RateLimitHetNganSach(FakeRateLimitPort):
    async def within_daily_budget(self, scope: ThreadScope) -> bool:
        return False


def _ctx() -> CallContext:
    return CallContext(
        scope=ThreadScope(platform="web", thread_id="t1"),
        sender_id="u1",
        trace_id="trace-test",
    )


def _envelope() -> ContextEnvelope:
    return ContextEnvelope(messages=(), tokens_used=0, has_knowledge=False)


async def _chay(llm: Any, **kwargs: Any):
    return await generate_with_verification(
        envelope=_envelope(),
        spec=OutputSpec(ma_the=MA_THE),
        verifier=PoemVerifier(),
        llm=llm,
        tools=FakeToolPort(),
        rate_limiter=kwargs.pop("rate_limiter", FakeRateLimitPort()),
        ctx=_ctx(),
        **kwargs,
    )


# ─────────────────── Tính chất cốt lõi: cổng không rò ───────────────────


@pytest.mark.asyncio
async def test_cong_KHONG_BAO_GIO_tra_bai_sai_luat():
    """Mô hình trả sai ở mọi lượt — không được có bất kỳ văn bản thơ nào đi ra."""
    llm = LlmTheoKichBan(BAI_SAI)

    kq = await _chay(llm, max_repair_rounds=3)

    assert is_err(kq)
    assert isinstance(kq.error, OutputKhongDat)
    # Bài sai không được rò qua bất cứ trường nào của đường trả về
    assert "Chiều rơi" not in kq.error.chan_doan
    assert kq.error.ma_the == MA_THE
    assert kq.error.so_luot_da_sua == 3


@pytest.mark.asyncio
async def test_loi_khong_dat_la_KHONG_dang_thu_lai():
    """Thử lại ở tầng job không giúp gì: vòng sửa đã thử hết lượt rồi."""
    kq = await _chay(LlmTheoKichBan(BAI_SAI), max_repair_rounds=1)
    assert is_retryable(kq.error) is False


@pytest.mark.asyncio
async def test_bai_dat_ngay_luot_dau_thi_KHONG_goi_lai_model():
    llm = LlmTheoKichBan(BAI_DAT)

    kq = await _chay(llm)

    assert is_ok(kq)
    assert kq.value.so_luot == 0
    assert llm.so_lan_goi == 1  # đúng một lần, không sửa thừa
    assert kq.value.text == BAI_DAT


@pytest.mark.asyncio
async def test_sua_dung_luot_thu_hai_thi_dat():
    llm = LlmTheoKichBan(BAI_SAI, BAI_DAT)

    kq = await _chay(llm)

    assert is_ok(kq)
    assert kq.value.so_luot == 1
    assert kq.value.ket_qua.dat is True


# ─────────────────── Biên bản gửi lại mô hình ───────────────────


@pytest.mark.asyncio
async def test_bien_ban_co_dia_chi_dong_va_ghim_dong_da_dat():
    llm = LlmTheoKichBan(BAI_SAI, BAI_DAT)

    await _chay(llm)

    # Lượt gọi thứ hai phải mang theo biên bản kiểm định
    lan_hai = llm.luot_nhan[1]
    van_ban = "\n".join(getattr(m, "content", "") for m in lan_hai)

    assert "<bien_ban_kiem_dinh>" in van_ban
    assert "D1" in van_ban and "D3" in van_ban  # địa chỉ dòng hỏng
    assert "8 tiếng" in van_ban and "4 tiếng" in van_ban  # số liệu cụ thể
    assert "GIỮ NGUYÊN" in van_ban  # ghim dòng đã đạt


@pytest.mark.asyncio
async def test_bien_ban_KHONG_duoc_vao_luot_system():
    """Trạng thái động không được mang thẩm quyền hệ thống."""
    llm = LlmTheoKichBan(BAI_SAI, BAI_DAT)

    await _chay(llm)

    for luot in llm.luot_nhan:
        for m in luot:
            assert type(m).__name__ != "SystemMessage"


# ─────────────────── Chặn G5, G6: không hội tụ ───────────────────


@pytest.mark.asyncio
async def test_khong_tien_bo_thi_LEO_THANG_chu_khong_sua_lai_cach_cu():
    """Hai lượt liên tiếp không giảm lỗi thì phải đổi chiến lược."""
    llm = LlmTheoKichBan(BAI_SAI, BAI_SAI_KHAC, BAI_SAI, BAI_SAI_KHAC)

    kq = await _chay(llm, max_repair_rounds=3)

    assert is_err(kq)
    # Chỉ dẫn gửi kèm phải leo tới nấc cuối, không lặp mãi "chỉ viết lại dòng bị nêu"
    chi_dan_da_dung = [
        cl
        for cl in THANG_LEO_THANG
        if any(
            CHI_DAN_SUA[cl] in getattr(m, "content", "")
            for luot in llm.luot_nhan
            for m in luot
        )
    ]
    assert "sinh_lai_ca_bai" in chi_dan_da_dung
    assert chi_dan_da_dung.index("sua_dong") < chi_dan_da_dung.index("sinh_lai_ca_bai")


@pytest.mark.asyncio
async def test_lap_lai_dung_bai_cu_thi_doi_chien_luoc_ngay():
    llm = LlmTheoKichBan(BAI_SAI, BAI_SAI, BAI_DAT)

    kq = await _chay(llm, max_repair_rounds=3)

    assert is_ok(kq)
    # Lượt 2 thấy lại đúng bài của lượt 1 -> G6 đẩy lên nấc mạnh hơn "sua_dong"
    assert kq.value.chien_luoc_cuoi != "sua_dong"


# ─────────────────── Chặn G3, G4: dừng có kiểm soát ───────────────────


@pytest.mark.asyncio
async def test_het_ngan_sach_thi_dung_ngay_KHONG_goi_model():
    llm = LlmTheoKichBan(BAI_DAT)

    kq = await _chay(llm, rate_limiter=RateLimitHetNganSach())

    assert is_err(kq)
    assert llm.so_lan_goi == 0


@pytest.mark.asyncio
async def test_co_dung_thi_KHONG_tra_bai_chua_kiem():
    llm = LlmTheoKichBan(BAI_SAI)

    kq = await _chay(llm, should_stop_hook=lambda: True)

    assert is_err(kq)
    assert isinstance(kq.error, OutputKhongDat)


# ─────────────────── Ràng buộc đến từ người dùng ───────────────────


@pytest.mark.asyncio
async def test_dung_luat_nhung_sai_so_dong_yeu_cau_thi_van_chua_dat():
    """F5 nói thể này không giới hạn số dòng, nhưng yêu cầu người dùng thì vẫn phải thoả."""
    llm = LlmTheoKichBan(BAI_DAT)

    kq = await generate_with_verification(
        envelope=_envelope(),
        spec=OutputSpec(ma_the=MA_THE, tham_so={"so_dong": 8}),
        verifier=PoemVerifier(),
        llm=llm,
        tools=FakeToolPort(),
        rate_limiter=FakeRateLimitPort(),
        ctx=_ctx(),
        max_repair_rounds=1,
    )

    assert is_err(kq)
    assert "YC1" in kq.error.chan_doan


# ─────────────────── Tool tự soi của vòng trong ───────────────────


def test_tool_tu_soi_dung_CHUNG_bo_luat_voi_cong_vong_ngoai():
    """Hai bộ luật song song là cách chắc chắn nhất để hai nơi nói hai điều khác nhau."""
    from adapters.tools import register_poem_check_tool
    from application.agent.tools.registry import tool_registry

    register_poem_check_tool()
    tool = tool_registry.get_tool("kiem_tra_tho")
    assert tool is not None

    ket_qua_tool = tool.func(van_ban=BAI_SAI)
    ket_qua_cong = PoemVerifier().kiem(BAI_SAI, OutputSpec(ma_the=MA_THE))

    assert ket_qua_tool["dat"] is ket_qua_cong.dat
    assert len(ket_qua_tool["vi_pham"]) == len(ket_qua_cong.loi)
