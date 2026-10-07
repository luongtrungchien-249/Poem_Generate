"""QĐ-TD-1 — tiêu đề, và hai bất biến không được phá.

    1. Tiêu đề KHÔNG đi qua luật thơ. Nó không phải một dòng thơ.
    2. Lượt đặt tiêu đề hỏng thì bài VẪN nguyên. Bài đã qua cổng trước khi lượt
       đó chạy; để một lượt gọi phụ đánh hỏng một bài đã đạt là đổi thứ chắc
       chắn lấy thứ trang trí.
"""

from __future__ import annotations

import pytest

from application.poetry.tieu_de import SO_TIENG_TOI_DA, dat_tieu_de, loc_tieu_de
from domain.common.errors import BotError
from domain.common.result import Err, Ok


class _LlmGia:
    """Mô hình giả: trả đúng thứ được dặn, hoặc nổ."""

    def __init__(self, tra_ve=None, no=False, loi=False):
        self.tra_ve, self.no, self.loi = tra_ve, no, loi
        self.so_lan_goi = 0

    async def reply(self, **kw):
        self.so_lan_goi += 1
        if self.no:
            raise RuntimeError("mạng hỏng")
        if self.loi:
            return Err(BotError(code="LLM_ERROR", message="quá tải"))
        return Ok(type("R", (), {"text": self.tra_ve})())


# ── Bộ lọc: thuần, test được mà không cần mô hình ───────────────────────────


@pytest.mark.parametrize(
    "tho, mong_doi",
    [
        ("Ghế Cũ Bên Thềm", "Ghế Cũ Bên Thềm"),
        ('"Ghế Cũ Bên Thềm"', "Ghế Cũ Bên Thềm"),
        ("**Ghế Cũ Bên Thềm**", "Ghế Cũ Bên Thềm"),
        ("Tiêu đề: Ghế Cũ", "Tiêu đề: Ghế Cũ"),  # lời dẫn dính liền -> giữ nguyên
        ("\n\n  Ghế Cũ Bên Thềm  \n", "Ghế Cũ Bên Thềm"),
        ("Ghế Cũ Bên Thềm.", "Ghế Cũ Bên Thềm"),
    ],
)
def test_loc_go_ky_tu_bao(tho, mong_doi):
    assert loc_tieu_de(tho) == mong_doi


def test_cau_dai_thi_BO_han_chu_khong_cat_ngan():
    """Cắt giữa chừng cho ra một mẩu vô nghĩa mà trông như có chủ ý."""
    dai = " ".join(["tiếng"] * (SO_TIENG_TOI_DA + 1))
    assert loc_tieu_de(dai) == ""


def test_rac_thi_rong():
    assert loc_tieu_de("") == ""
    assert loc_tieu_de("   \n  \n ") == ""


# ── Bất biến 2: hỏng thì rỗng, KHÔNG ném lỗi ────────────────────────────────


@pytest.mark.asyncio
async def test_llm_no_thi_tra_RONG_khong_nem():
    """⛔ Bài đã qua cổng rồi. Không lỗi nào ở đây đáng đánh hỏng nó."""
    assert await dat_tieu_de("một dòng thơ", llm=_LlmGia(no=True), ctx=None) == ""


@pytest.mark.asyncio
async def test_llm_tra_Err_thi_tra_RONG():
    assert await dat_tieu_de("một dòng thơ", llm=_LlmGia(loi=True), ctx=None) == ""


@pytest.mark.asyncio
async def test_bai_rong_thi_KHONG_goi_mo_hinh():
    """Không có bài thì không có gì để đặt tên — đừng tốn một lượt gọi."""
    llm = _LlmGia(tra_ve="X")
    assert await dat_tieu_de("   ", llm=llm, ctx=None) == ""
    assert llm.so_lan_goi == 0


@pytest.mark.asyncio
async def test_duong_hanh_phuc():
    llm = _LlmGia(tra_ve="Ghế Cũ Bên Thềm")
    assert await dat_tieu_de("một dòng thơ", llm=llm, ctx=None) == "Ghế Cũ Bên Thềm"


# ── Bất biến 1: tiêu đề không dính gì tới luật thơ ──────────────────────────


def test_module_KHONG_goi_rule():
    """⛔ Tiêu đề không phải một dòng thơ: không đếm tiếng, không khuôn, không vần.

    Ghim bằng cây cú pháp chứ không bằng mắt: một `import` lọt vào đây là dấu hiệu
    ai đó bắt đầu bắt tiêu đề chịu luật thơ.
    """
    import ast
    from pathlib import Path

    import application.poetry.tieu_de as mod

    cay = ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
    for nut in ast.walk(cay):
        if isinstance(nut, ast.ImportFrom):
            assert "rule" not in (nut.module or ""), nut.module
