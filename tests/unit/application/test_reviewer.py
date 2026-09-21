"""QĐ-RV-1 — node Reviewer chấm nội dung, và bất biến duy nhất của nó.

    TƯ VẤN, KHÔNG CHẶN.

`quality.py` giải thích vì sao: port `OutputVerifier` đòi ĐỒNG BỘ, THUẦN, TẤT ĐỊNH
— "cổng chặn không được phép trượt vì mạng", và "nếu không tất định, vòng sửa sẽ
dao động". Một LLM-judge vi phạm cả hai.

`compare_prompt.py` chính là hệ thống mắc đúng lỗi đó: LLM chấm rồi sửa theo điểm
LLM vừa chấm. Test đầu tiên dưới đây tồn tại để điều đó không tái diễn ở đây.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from application.poetry.reviewer import (
    CHI_DAN_REVIEWER,
    NhanXetReviewer,
    doc_nhan_xet,
    xin_nhan_xet,
)
from domain.common.errors import BotError
from domain.common.result import Err, Ok

GOC_SRC = Path(__file__).resolve().parents[3] / "src"


class _LlmGia:
    def __init__(self, tra_ve="", no=False, loi=False):
        self.tra_ve, self.no, self.loi = tra_ve, no, loi
        self.so_lan_goi = 0

    async def reply(self, **kw):
        self.so_lan_goi += 1
        if self.no:
            raise RuntimeError("mạng hỏng")
        if self.loi:
            return Err(BotError(code="LLM_ERROR", message="quá tải"))
        return Ok(type("R", (), {"text": self.tra_ve})())


# ── 🔴 BẤT BIẾN: không đường nào nối Reviewer vào cổng chặn ─────────────────


def test_reviewer_khong_noi_vao_cong_chan():
    """⛔ Ghim CHIỀU IMPORT, không ghim lời hứa trong chú thích.

    Nếu `verify_output.py` hay `quality.py` một ngày nào đó import Reviewer, nghĩa
    là ai đó vừa nối một lượt gọi mạng vào một cổng phải tất định.
    """
    for ten in ("pipeline/stages/verify_output.py", "poetry/quality.py"):
        cay = ast.parse((GOC_SRC / "application" / ten).read_text(encoding="utf-8"))
        for nut in ast.walk(cay):
            mod = getattr(nut, "module", None) or ""
            assert "reviewer" not in mod, f"{ten} đã import reviewer"
            if isinstance(nut, ast.Import):
                for a in nut.names:
                    assert "reviewer" not in a.name, ten


def test_nhan_xet_KHONG_co_truong_dat_hay_truot():
    """Không có `dat` thì không ai lỡ tay dùng nó để chặn bài."""
    truong = set(NhanXetReviewer.__dataclass_fields__)
    assert truong == {"co_y_kien", "mach_lac", "hinh_anh", "nhan_xet"}


def test_reviewer_KHONG_cham_thi_luat():
    """Chấm thi luật bằng LLM là dựng thẩm quyền thứ hai bên cạnh `rule.py`."""
    assert "KHÔNG chấm thi luật" in CHI_DAN_REVIEWER
    for dau_hieu in ("B T B", "T B T", "7 tiếng", "bội của 4"):
        assert dau_hieu not in CHI_DAN_REVIEWER, dau_hieu


def test_co_mo_neo_hieu_chuan():
    """Phần duy nhất nhập từ bản prompt cũ — neo từng mốc, chống điểm phồng."""
    for moc in ("10", "8", "5", "1"):
        assert moc in CHI_DAN_REVIEWER
    assert "trung bình" in CHI_DAN_REVIEWER


def test_KHONG_nhap_trong_so_cua_ban_cu():
    """Bốn con số 0,25/0,25/0,35/0,15 không có nguồn gốc — chép lại là vi phạm N1."""
    for so in ("0.25", "0,25", "0.35", "0,35", "0.15", "w="):
        assert so not in CHI_DAN_REVIEWER, so


# ── Bộ đọc: thuần ───────────────────────────────────────────────────────────


def test_doc_du_hai_chieu():
    kq = doc_nhan_xet(
        "<mach_lac>7</mach_lac><hinh_anh>4.5</hinh_anh>"
        "<nhan_xet>Dòng 3 rời khỏi mạch.</nhan_xet>"
    )
    assert kq.co_y_kien and kq.mach_lac == 7.0 and kq.hinh_anh == 4.5
    assert kq.nhan_xet == "Dòng 3 rời khỏi mạch."


def test_diem_ngoai_thang_thi_coi_nhu_KHONG_DOC_DUOC():
    """⛔ Không kẹp về biên: kẹp là bịa một con số mô hình không nói."""
    kq = doc_nhan_xet("<mach_lac>42</mach_lac><hinh_anh>6</hinh_anh>")
    assert kq.mach_lac is None
    assert kq.hinh_anh == 6.0


def test_rac_hoan_toan_thi_KHONG_CO_y_kien():
    """Khác hẳn 'có ý kiến và điểm thấp' — người đọc phải phân biệt được."""
    assert doc_nhan_xet("xin lỗi, tôi không chấm được").co_y_kien is False


# ── Hỏng thì im lặng, không ném ─────────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.parametrize("llm", [_LlmGia(no=True), _LlmGia(loi=True)])
async def test_hong_thi_khong_co_y_kien(llm):
    assert (await xin_nhan_xet("thơ", llm=llm, ctx=None)).co_y_kien is False


@pytest.mark.asyncio
async def test_bai_rong_thi_khong_goi_mo_hinh():
    llm = _LlmGia(tra_ve="<mach_lac>9</mach_lac>")
    assert (await xin_nhan_xet("  ", llm=llm, ctx=None)).co_y_kien is False
    assert llm.so_lan_goi == 0
