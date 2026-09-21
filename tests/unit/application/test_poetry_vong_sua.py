"""Cổng đầy đủ CHẠY THẬT trong vòng sửa `generate_with_verification`.

Test đơn vị chứng minh từng mảnh đúng. File này chứng minh điều khác và mạnh hơn:
ba chỉ thị của chủ dự án có hiệu lực trên ĐƯỜNG THẬT, không chỉ khi gọi trực tiếp.

    chỉ thị 2  sáu bước suy luận chặn được ngay trong vòng sửa
    chỉ thị 3  chất lượng kém -> khung CoT thực sự đi vào lượt `user` gửi mô hình
    chỉ thị 5  thiếu thông tin -> không bài thơ nào đi ra, kể cả bài đúng luật
"""

from __future__ import annotations

from typing import Any

import pytest

from application.pipeline.stages.verify_output import generate_with_verification
from application.poetry.cot import THE_CoT
from application.poetry.requirement import PoetryRequirement, mac_dinh, nguoi_dung
from application.poetry.verifier import PoemVerifierDayDu
from application.ports.llm import CallContext, UserMessage
from application.ports.verifier import OutputSpec
from application.prompting.context import ContextEnvelope
from domain.common.errors import OutputKhongDat
from domain.common.result import is_err, is_ok
from domain.conversation.thread import ThreadScope
from tests.fakes.ports import FakeRateLimitPort, FakeToolPort
from tests.unit.application.test_verify_output import LlmTheoKichBan

pytestmark = pytest.mark.unit

BAI_TAI_LIEU = (
    "Chiều rơi chậm xuống mái rêu xanh\n"
    "Gió cuốn heo may lạc cuối ghềnh\n"
    "Một bóng con đò trôi lặng lẽ\n"
    "Sông dài ôm trọn mảnh trời xanh"
)
# Đúng luật nhưng MỌI DÒNG Y HỆT — luật không bắt được, chất lượng phải bắt.
# (Ví dụ cũ "lặp nguyên khổ" nay qua được: đó là điệp khổ, S20 cho phép.)
BAI_KEM_CHAT_LUONG = "\n".join(["Trời cao mây biếc xanh ngời cành"] * 8)

BAI_DAT_8_DONG = (
    "Chiều rơi chậm xuống mái rêu xanh\n"
    "Gió cuốn heo may lạc cuối ghềnh\n"
    "Một bóng con đò trôi lặng lẽ\n"
    "Sông dài ôm trọn mảnh trời xanh\n"
    "Đường cũ chân ai còn vọng lại\n"
    "Bờ tre nghiêng bóng nắng chưa đành\n"
    "Người đi để lại mùa hương cũ\n"
    "Khói bếp chiều nay vẫn quẩn quanh"
)


def _req(so_dong: int) -> PoetryRequirement:
    return PoetryRequirement(
        chu_de=nguoi_dung("chiều sông"),
        so_dong=nguoi_dung(so_dong),
        cam_xuc=nguoi_dung("lặng"),
        phong_cach=mac_dinh("cổ điển"),
        rang_buoc_van=mac_dinh("vần chân"),
        rang_buoc_thanh=mac_dinh("luân phiên"),
    )


def _ctx() -> CallContext:
    return CallContext(
        scope=ThreadScope(platform="web", thread_id="t1"),
        sender_id="u1",
        trace_id="trace-poetry",
    )


async def _chay(llm: Any, tham_so: dict[str, Any], **kw: Any):
    return await generate_with_verification(
        envelope=ContextEnvelope(messages=(), tokens_used=0, has_knowledge=False),
        spec=OutputSpec(ma_the="that_ngon_tu_do", tham_so=tham_so),
        verifier=PoemVerifierDayDu(),
        llm=llm,
        tools=FakeToolPort(),
        rate_limiter=FakeRateLimitPort(),
        ctx=_ctx(),
        **kw,
    )


@pytest.mark.asyncio
async def test_khung_CoT_that_su_di_vao_luot_gui_mo_hinh():
    """Chỉ thị 3 trên đường thật.

    Mô hình trả một bài ĐÚNG LUẬT nhưng lặp khổ. Luật không có gì để nói; chất
    lượng phải bắt, và khung suy luận bốn ô phải đi vào lượt `user` của lượt sau.
    """
    llm = LlmTheoKichBan(BAI_KEM_CHAT_LUONG)
    kq = await _chay(
        llm, {"yeu_cau": _req(8), "chu_de": "chiều sông"}, max_repair_rounds=1
    )

    assert is_err(kq), "bài mọi dòng y hệt không được phép đi ra"
    assert isinstance(kq.error, OutputKhongDat)

    # Lượt thứ hai phải chứa khung CoT do vòng sửa chèn vào.
    assert len(llm.luot_nhan) >= 2, "phải có ít nhất một lượt sửa"
    luot_sua = llm.luot_nhan[-1]
    van_ban_user = "\n".join(
        m.content for m in luot_sua if isinstance(m, UserMessage)
    )
    assert THE_CoT in van_ban_user, "khung suy luận phải đi vào lượt user"
    for o in ("1. CHIỀU CHƯA ĐẠT", "2. NGUYÊN NHÂN", "3. HƯỚNG SỬA", "4. DÒNG PHẢI GIỮ NGUYÊN"):
        assert o in van_ban_user


@pytest.mark.asyncio
async def test_thieu_thong_tin_thi_KHONG_bai_nao_di_ra_ke_ca_bai_dung_luat():
    """Chỉ thị 5, dạng mạnh nhất — trên đường thật.

    Mô hình trả một bài hoàn toàn đúng luật VÀ đủ chất lượng. Nhưng yêu cầu chưa
    đủ thông tin, nên B1 chặn và không gì đi ra.
    """
    llm = LlmTheoKichBan(BAI_DAT_8_DONG)
    kq = await _chay(
        llm,
        {"yeu_cau": PoetryRequirement(van_ban_goc="Viết cho tôi một bài thơ.")},
        max_repair_rounds=1,
    )
    assert is_err(kq)
    assert isinstance(kq.error, OutputKhongDat)


@pytest.mark.asyncio
async def test_bai_du_luat_du_chat_luong_du_thong_tin_thi_qua():
    """Ca thuận: cả ba chỉ thị thoả thì bài đi ra bình thường."""
    llm = LlmTheoKichBan(BAI_DAT_8_DONG)
    kq = await _chay(llm, {"yeu_cau": _req(8), "chu_de": "chiều sông"})

    assert is_ok(kq), f"lẽ ra phải qua; kịch bản gọi {llm.so_lan_goi} lượt"
    assert kq.value.text.strip() == BAI_DAT_8_DONG
    assert kq.value.so_luot == 0
    assert kq.value.ket_qua.dat


@pytest.mark.asyncio
async def test_mo_hinh_sua_duoc_sau_khi_nhan_khung_CoT():
    """Vòng sửa hội tụ: lượt 1 lặp khổ, lượt 2 sửa xong."""
    llm = LlmTheoKichBan(BAI_KEM_CHAT_LUONG, BAI_DAT_8_DONG)
    kq = await _chay(llm, {"yeu_cau": _req(8), "chu_de": "chiều sông"})

    assert is_ok(kq)
    assert kq.value.so_luot == 1, "phải mất đúng một lượt sửa"
    assert kq.value.text.strip() == BAI_DAT_8_DONG


@pytest.mark.asyncio
async def test_rule_py_van_la_nguoi_phan_cuoi_cung_ve_luat():
    """Chỉ thị 1: dù có thêm tầng chất lượng, luật vẫn do rule.py phán.

    Bài sai số tiếng phải bị chặn bởi mã H1 của tài liệu luật, KHÔNG phải bởi một
    mã chất lượng nào đó — nếu không thì tầng mới đã âm thầm thay quyền của luật.
    """
    sai = "\n".join(["Một dòng sáu tiếng thôi mà"] * 4)
    llm = LlmTheoKichBan(sai)
    kq = await _chay(llm, {"yeu_cau": _req(4)}, max_repair_rounds=0)

    assert is_err(kq)
    bb = PoemVerifierDayDu().lap_bien_ban(
        sai, OutputSpec(ma_the="that_ngon_tu_do", tham_so={"yeu_cau": _req(4)})
    )
    assert not bb.dat_luat
    assert any(vp.ma in ("H1", "H2") for vp in bb.verdict.vi_pham)
    assert bb.suy_luan.buoc_dung_lai == "B4", "phải dừng ở bước LUẬT, không phải bước chất lượng"
