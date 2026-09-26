"""QĐ-P2 — bài có một dòng trùng NGUYÊN VĂN thơ đã có thì bị chặn.

Chặn ở CHẤT LƯỢNG, không ở luật: `dat_luat` vẫn đúng, chỉ `dat` sai.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from adapters.persistence.corpus.chi_muc_dong import ChiMucDongTho
from application.poetry.doi_chieu_chep import khoa_dong, tim_dong_chep
from application.poetry.requirement import PoetryRequirement, mac_dinh, nguoi_dung
from application.poetry.verifier import PoemVerifierDayDu
from application.ports.chi_muc_tho import NguonDong
from application.ports.verifier import OutputSpec

pytestmark = pytest.mark.unit

GOC = Path(__file__).resolve().parents[3]
DAT = """Chiều rơi chậm xuống mái rêu xanh
Con ngõ nhỏ dài hơn tiếng ve
Ai đứng bên kia bờ nắng mảnh
Gọi một mùa xa chẳng dám về"""
SPEC = OutputSpec(
    ma_the="that_ngon_tu_do",
    tham_so={
        "so_dong": 4,
        "yeu_cau": PoetryRequirement(
            chu_de=nguoi_dung("chiều quê"), so_dong=nguoi_dung(4), cam_xuc=nguoi_dung("nhớ"),
            phong_cach=mac_dinh(None), rang_buoc_van=mac_dinh(None),
            rang_buoc_thanh=mac_dinh(None), van_ban_goc="Viết bài 4 dòng về chiều quê",
        ),
    },
)


class _ChiMucGia:
    def __init__(self, *dong: str) -> None:
        self._k = {khoa_dong(d): NguonDong(kho="hf", tieu_de="Bài có sẵn", tac_gia="X") for d in dong}

    def tim(self, khoa: str) -> NguonDong | None:
        return self._k.get(khoa)


def test_khoa_bo_dau_cau_va_hoa_thuong_nhung_giu_thanh():
    assert khoa_dong("Chiều rơi chậm, xuống mái rêu xanh!") == khoa_dong("chiều rơi chậm xuống mái rêu xanh")
    assert khoa_dong("Chiều rơi chậm xuống mái rêu xanh") != khoa_dong("Chiều rơi chậm xuống mái rêu xánh")
    assert khoa_dong("tám tiếng thì không phải dòng của thể này đâu") is None


def test_tim_dung_dong_va_dia_chi():
    ra = tim_dong_chep(DAT, _ChiMucGia("Ai đứng bên kia bờ nắng mảnh"))
    assert [(so, n.kho) for so, _, n in ra] == [(3, "hf")]
    assert tim_dong_chep(DAT, None) == ()


def test_verifier_chan_bai_chep_nhung_KHONG_noi_sai_luat():
    v = PoemVerifierDayDu(chi_muc_chep=_ChiMucGia("Gọi một mùa xa chẳng dám về"))
    bb = v.lap_bien_ban(DAT, SPEC)
    assert bb.dat_luat and not bb.dat
    kq = v.kiem(DAT, SPEC)
    assert not kq.dat
    assert [(x.ma, x.dia_chi) for x in kq.loi if x.ma == "CHEP"] == [("CHEP", "D4")]
    assert "D4" in kq.bien_ban and "Bài có sẵn" in kq.bien_ban


def test_khong_chi_muc_thi_hanh_vi_cu_giu_nguyen():
    assert PoemVerifierDayDu().kiem(DAT, SPEC).dat == PoemVerifierDayDu(
        chi_muc_chep=_ChiMucGia()
    ).kiem(DAT, SPEC).dat


def test_chi_muc_luu_roi_nap_lai_cho_cung_ket_qua(tmp_path):
    nguon = tmp_path / "kho.jsonl"
    nguon.write_text(json.dumps({"poem": DAT, "title": "Ví dụ §11", "author": "A"}, ensure_ascii=False) + "\n",
                     encoding="utf-8")
    goc = ChiMucDongTho.tu_jsonl(((nguon, "hf", "poem"),))
    assert goc.so_dong == 4
    tep = tmp_path / "cm.bin"
    goc.luu(tep)
    nap_lai = ChiMucDongTho.tu_tep_hoac_lui(tep, ())
    n = nap_lai.tim(khoa_dong("Con ngõ nhỏ dài hơn tiếng ve") or "")
    assert n == NguonDong(kho="hf", tieu_de="Ví dụ §11", tac_gia="A", url="")


def test_thieu_tep_dung_san_thi_lui_ve_nguon_nho(tmp_path):
    cm = ChiMucDongTho.tu_tep_hoac_lui(
        tmp_path / "khong_co.bin",
        ((GOC / "datalake" / "corpus_tuyen" / "tho_mau.jsonl", "tho_mau", "tho"),),
    )
    assert cm.so_dong > 0  # vẫn bắt được chép BÀI MẪU trên checkout sạch
