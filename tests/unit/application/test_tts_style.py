"""Hướng dẫn giọng đọc — chủ dự án chốt 22/09/2026.

Nhập từ `compare_prompt.py` (`TTS_STYLE_*`). Hai bất biến y hệt `tieu_de.py`:
không đi qua luật thơ, và hỏng thì trả rỗng chứ không đánh hỏng bài đã đạt.

⚠️ File này KHÔNG mâu thuẫn QĐ-TTS-1: quyết định ấy đóng phần PHIÊN ÂM (đổi số
tiếng, tức đụng H1), không đóng phần hướng dẫn cách đọc một bài đã xong.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from application.poetry.tts_style import (
    SO_TIENG_TOI_DA,
    huong_dan_doc,
    loc_huong_dan,
)
from application.ports.llm import CallContext
from application.prompting.system import CHI_DAN_HUONG_DAN_DOC
from domain.common.errors import BotError
from domain.common.result import Err, Ok
from domain.conversation.thread import ThreadScope

NGUON = Path(__file__).resolve().parents[3] / "src/application/poetry/tts_style.py"

BAI = (
    "Chiều rơi chậm xuống mái rêu xanh\n"
    "Con ngõ nhỏ dài hơn tiếng ve\n"
    "Ai đứng bên kia bờ nắng mảnh\n"
    "Gọi một mùa xa chẳng dám về"
)


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


def _ctx():
    return CallContext(
        scope=ThreadScope(platform="web", thread_id="t1"),
        sender_id="u1",
        trace_id="tr",
    )


# ── 🔴 BẤT BIẾN 1: không đi qua luật thơ ────────────────────────────────────


def test_KHONG_goi_rule_py():
    """Hướng dẫn đọc không phải một dòng thơ. Đếm tiếng nó là vô nghĩa."""
    cay = ast.parse(NGUON.read_text(encoding="utf-8"))
    ten = {
        n.module for n in ast.walk(cay) if isinstance(n, ast.ImportFrom) and n.module
    }
    assert not any("rule" in (t or "") for t in ten), ten


def test_chi_dan_KHONG_nhac_luat_tho():
    """Nhắc số tiếng hay khuôn thanh ở đây là dựng nguồn luật thứ hai."""
    for dau_hieu in ("7 tiếng", "bảy tiếng", "B T B", "T B T", "bội của 4", "vần chân"):
        assert dau_hieu not in CHI_DAN_HUONG_DAN_DOC, dau_hieu


# ── 🔴 BẤT BIẾN 2: hỏng thì rỗng, không bao giờ ném ─────────────────────────


@pytest.mark.asyncio
@pytest.mark.parametrize("llm", [_LlmGia(no=True), _LlmGia(loi=True), _LlmGia("")])
async def test_moi_nhanh_hong_deu_ve_CHUOI_RONG(llm):
    """Bài đã qua cổng rồi. Không lỗi nào ở đây đáng để đánh hỏng nó."""
    assert await huong_dan_doc(BAI, llm=llm, ctx=_ctx()) == ""


@pytest.mark.asyncio
async def test_bai_rong_thi_KHONG_goi_mo_hinh():
    """Không có bài thì không có gì để hướng dẫn — đừng tốn một lượt gọi."""
    llm = _LlmGia("gì đó")
    assert await huong_dan_doc("   ", llm=llm, ctx=_ctx()) == ""
    assert llm.so_lan_goi == 0


# ── Bộ đọc kết quả: thuần, test được không cần mô hình ──────────────────────


def test_gop_NHIEU_DONG_thanh_mot_doan():
    """⛔ Khác `tieu_de.loc_tieu_de` ở đúng chỗ này.

    Tiêu đề là MỘT dòng nên lấy dòng đầu. Hướng dẫn đọc là đoạn văn xuôi — lấy
    dòng đầu sẽ cắt cụt đúng phần nội dung.
    """
    ra = loc_huong_dan("Đọc chậm rãi, giọng trầm.\nNhấn nhẹ ở tiếng cuối mỗi dòng.")
    assert "trầm" in ra and "tiếng cuối" in ra


def test_qua_dai_thi_BO_chu_khong_cat_ngan():
    """Cắt giữa chừng cho ra một mẩu cụt mà trông như có chủ ý."""
    assert loc_huong_dan(" ".join(["tiếng"] * (SO_TIENG_TOI_DA + 1))) == ""


def test_got_ky_tu_bao_quanh():
    assert loc_huong_dan('"Đọc chậm rãi."') == "Đọc chậm rãi."


def test_rac_hoan_toan_thi_rong():
    assert loc_huong_dan("   \n\n  ") == ""


# ── Điều kiện 2 của `instructions.py`: phải có mã đọc nó NGAY ───────────────


def test_truong_di_HET_toi_response_API():
    """⛔ Thêm hằng số mà không có đường dẫn tới người dùng là dựng mã chết.

    Đúng thứ vừa xảy ra với Reviewer: viết đủ, test đủ, không ai gọi.
    """
    import dataclasses

    from application.poetry.sinh_tho import DaSinhTho
    from contracts.poem import PoemResponse

    assert "huong_dan_doc" in {f.name for f in dataclasses.fields(DaSinhTho)}
    assert "huong_dan_doc" in PoemResponse.model_fields

    router = (
        Path(__file__).resolve().parents[3]
        / "src/entrypoints/api/routers/poem.py"
    ).read_text(encoding="utf-8")
    assert "huong_dan_doc=ra.huong_dan_doc" in router
