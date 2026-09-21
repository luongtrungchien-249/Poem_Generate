"""§7.2 Requirement Analyzer — trích yêu cầu từ câu nói tự nhiên.

Điều phải chứng minh KHÔNG phải "trích được", mà là điều khó hơn:

    Mô hình KHÔNG THỂ tuyên bố người dùng đã nói điều họ chưa nói.

Cơ chế: bắt trích dẫn nguyên văn, rồi kiểm đoạn trích ấy có thật trong câu người
dùng không. Bịa trích dẫn thì trường bị hạ xuống `suy_doan`, và cổng B1 chặn.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from application.poetry.phan_tich_yeu_cau import (
    phan_tich_tho,
    phan_tich_yeu_cau,
    trich_so_dong,
)
from application.poetry.requirement import CanHoi, danh_gia_du_thong_tin
from application.ports.llm import CallContext
from domain.common.errors import UpstreamError
from domain.common.result import Err, Ok, is_ok
from domain.conversation.thread import ThreadScope

pytestmark = pytest.mark.unit


def _ctx() -> CallContext:
    return CallContext(
        scope=ThreadScope(platform="web", thread_id="t"), sender_id="u", trace_id="tr"
    )


class LlmTraJson:
    def __init__(self, payload: Any) -> None:
        self.payload = payload

    async def reply(self, *a: Any, **kw: Any) -> Any:  # pragma: no cover
        raise AssertionError("không dùng reply")

    async def cheap(self, messages: Any, route: Any, ctx: Any) -> Any:
        if isinstance(self.payload, str):
            return Ok(self.payload)
        return Ok(json.dumps(self.payload, ensure_ascii=False))


class LlmHong:
    async def reply(self, *a: Any, **kw: Any) -> Any:  # pragma: no cover
        raise AssertionError("không dùng reply")

    async def cheap(self, *a: Any, **kw: Any) -> Any:
        return Err(UpstreamError(upstream="fake", message="mạng hỏng"))


# ── Số dòng: tất định, không giao cho mô hình ────────────────────────────────


@pytest.mark.parametrize(
    "cau,mong",
    [
        ("Viết bài 8 dòng về quê", 8),
        ("làm cho tôi 12 câu thơ", 12),
        ("bài thơ tám dòng nhé", 8),
        ("mười sáu dòng về mùa thu", 16),
        ("viết bài thơ về biển", None),
        ("viết bài thơ thật dài", None),
    ],
)
def test_trich_so_dong_tat_dinh(cau: str, mong: int | None):
    assert trich_so_dong(cau) == mong


def test_KHONG_suy_dien_so_dong_tu_tu_mo_ho():
    """'ngắn'/'dài' không có nghĩa đo được. Đoán ở đây là đoán đúng chỗ H4 không tha."""
    assert trich_so_dong("viết bài thơ ngắn thôi") is None
    assert phan_tich_tho("viết bài thơ ngắn thôi").so_dong.gia_tri is None


def test_phan_tich_tho_chay_duoc_khong_can_mo_hinh():
    req = phan_tich_tho("Viết 8 dòng về quê hương")
    assert req.so_dong_int == 8
    assert req.so_dong.nguon == "nguoi_dung"


# ── Cơ chế trích dẫn: nhãn `nguon` phải KIỂM ĐƯỢC ────────────────────────────


@pytest.mark.asyncio
async def test_trich_dan_CO_THAT_thi_nguon_la_nguoi_dung():
    cau = "Viết bài thơ 8 dòng về quê hương, giọng hoài niệm"
    llm = LlmTraJson(
        {
            "chu_de": {"gia_tri": "quê hương", "trich": "về quê hương"},
            "cam_xuc": {"gia_tri": "hoài niệm", "trich": "giọng hoài niệm"},
        }
    )
    kq = await phan_tich_yeu_cau(cau, llm=llm, ctx=_ctx())
    assert is_ok(kq)
    req = kq.value.yeu_cau
    assert req.chu_de.nguon == "nguoi_dung"
    assert req.cam_xuc.nguon == "nguoi_dung"
    assert kq.value.truong_suy_doan == ()


@pytest.mark.asyncio
async def test_trich_dan_BIA_RA_thi_bi_ha_xuong_suy_doan():
    """⛔ Ca trung tâm. Mô hình đoán chủ đề rồi bịa một trích dẫn không có thật."""
    cau = "Viết cho tôi một bài thơ 8 dòng"
    llm = LlmTraJson(
        {"chu_de": {"gia_tri": "mùa thu", "trich": "về mùa thu Hà Nội"}}
    )
    kq = await phan_tich_yeu_cau(cau, llm=llm, ctx=_ctx())
    assert is_ok(kq)
    assert "chu_de" in kq.value.truong_suy_doan
    assert kq.value.yeu_cau.chu_de.nguon == "suy_doan"


@pytest.mark.asyncio
async def test_truong_suy_doan_bi_cong_B1_CHAN():
    """Cả chuỗi phải khớp: trích bịa -> suy_doan -> cổng hỏi lại, không sinh thơ."""
    cau = "Viết cho tôi một bài thơ 8 dòng"
    llm = LlmTraJson({"chu_de": {"gia_tri": "mùa thu", "trich": "không có trong câu"}})
    kq = await phan_tich_yeu_cau(cau, llm=llm, ctx=_ctx())
    cong = danh_gia_du_thong_tin(kq.value.yeu_cau)
    assert isinstance(cong, CanHoi)
    assert cong.ca == 0, "trường suy đoán phải bị chặn ở ca 0"


@pytest.mark.asyncio
async def test_trich_rong_thi_de_TRONG_chu_khong_doan():
    cau = "Viết bài thơ 8 dòng về biển"
    llm = LlmTraJson(
        {
            "chu_de": {"gia_tri": "biển", "trich": "về biển"},
            "cam_xuc": {"gia_tri": "", "trich": ""},
        }
    )
    kq = await phan_tich_yeu_cau(cau, llm=llm, ctx=_ctx())
    req = kq.value.yeu_cau
    assert req.chu_de.co_gia_tri
    assert not req.cam_xuc.co_gia_tri


@pytest.mark.asyncio
async def test_trich_dan_bo_qua_hoa_thuong_va_khoang_trang():
    cau = "Viết bài thơ   8 dòng  về  Quê Hương"
    llm = LlmTraJson({"chu_de": {"gia_tri": "quê hương", "trich": "về Quê  Hương"}})
    kq = await phan_tich_yeu_cau(cau, llm=llm, ctx=_ctx())
    assert kq.value.yeu_cau.chu_de.nguon == "nguoi_dung"


# ── §32 LLM Failure: hỏng thì lùi, không sập ─────────────────────────────────


@pytest.mark.asyncio
async def test_mo_hinh_hong_thi_lui_ve_regex():
    kq = await phan_tich_yeu_cau("Viết 8 dòng về quê", llm=LlmHong(), ctx=_ctx())
    assert is_ok(kq)
    assert kq.value.chi_co_regex
    assert kq.value.yeu_cau.so_dong_int == 8


@pytest.mark.asyncio
async def test_mo_hinh_tra_rac_thi_lui_ve_regex():
    kq = await phan_tich_yeu_cau(
        "Viết 8 dòng về quê", llm=LlmTraJson("xin chào, tôi không biết"), ctx=_ctx()
    )
    assert is_ok(kq)
    assert kq.value.chi_co_regex
    assert kq.value.yeu_cau.so_dong_int == 8


@pytest.mark.asyncio
async def test_doc_duoc_json_boc_trong_rao_markdown():
    llm = LlmTraJson(
        '```json\n{"chu_de": {"gia_tri": "biển", "trich": "về biển"}}\n```'
    )
    kq = await phan_tich_yeu_cau("Viết 8 dòng về biển", llm=llm, ctx=_ctx())
    assert kq.value.yeu_cau.chu_de.gia_tri == "biển"


@pytest.mark.asyncio
async def test_so_dong_cua_mo_hinh_KHONG_ghi_de_regex():
    """H4 là luật cứng; con số phải đến từ phép trích tất định."""
    llm = LlmTraJson(
        {"so_dong": {"gia_tri": "100", "trich": "8 dòng"},
         "chu_de": {"gia_tri": "biển", "trich": "về biển"}}
    )
    kq = await phan_tich_yeu_cau("Viết 8 dòng về biển", llm=llm, ctx=_ctx())
    assert kq.value.yeu_cau.so_dong_int == 8
