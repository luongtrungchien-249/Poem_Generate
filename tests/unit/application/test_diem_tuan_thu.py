"""Plan_PoeTone GĐ1.1 — điểm tuân thủ liên tục MÔ TẢ khoảng cách tới đích, không phán.

Bất biến quan trọng nhất: điểm "trọn vẹn" phải trùng khít với `rule.py` nói ĐẠT.
Đã đối chiếu 26/09/2026 trên 3.000 bài `bai_dat.jsonl` (đều trọn vẹn) và 23.120 bài
trượt của kho HF (không bài nào trọn vẹn). Test dưới giữ điều đó trên ngữ liệu
commit được.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from application.poetry.diem_tuan_thu import do_diem_tuan_thu
from application.rule import kiem_tra_bai_tho

pytestmark = pytest.mark.unit

GOC = Path(__file__).resolve().parents[3]

# Ví dụ §11 của tài liệu luật — đạt.
DAT = """Chiều rơi chậm xuống mái rêu xanh
Con ngõ nhỏ dài hơn tiếng ve
Ai đứng bên kia bờ nắng mảnh
Gọi một mùa xa chẳng dám về"""


def test_bai_dat_thi_tron_ven():
    assert kiem_tra_bai_tho(DAT).dat
    d = do_diem_tuan_thu(DAT)
    assert d.tron_ven
    assert (d.cau_truc, d.thanh, d.van, d.so_dong_can_sua) == (1.0, 1.0, 1.0, 0)


def test_sai_mot_dong_thanh_tru_dung_mot_phan_tu():
    # D1 đổi "xuống" (T, P4) thành "trên" (B): vẫn 7 tiếng, hỏng khuôn.
    bai = DAT.replace("chậm xuống mái", "chậm trên mái")
    d = do_diem_tuan_thu(bai)
    assert d.cau_truc == 1.0
    assert d.thanh == 0.75
    assert d.so_dong_can_sua == 1
    assert not kiem_tra_bai_tho(bai).dat


def test_so_duoc_hai_ung_vien_chet_o_hai_tang_khac_nhau():
    """Lý do file này tồn tại: `len(vi_pham)` không so được hai ca này."""
    chet_tang_2 = DAT.replace("Chiều rơi chậm", "Chiều rơi rất chậm")  # 1 dòng 8 tiếng
    chet_tang_4 = DAT.replace("chậm xuống mái", "chậm trên mái").replace(
        "Con ngõ nhỏ", "Con đường nhỏ"
    )  # 2 dòng sai thanh
    v2, v4 = kiem_tra_bai_tho(chet_tang_2), kiem_tra_bai_tho(chet_tang_4)
    assert v2.tang_dung_lai == 2 and v4.tang_dung_lai == 4
    k2 = do_diem_tuan_thu(chet_tang_2).khoa_xep_hang()
    k4 = do_diem_tuan_thu(chet_tang_4).khoa_xep_hang()
    assert k2 < k4  # 1 dòng phải viết lại < 2 dòng


def test_hinh_thuc_sai_xep_sau_moi_thu():
    ba_dong = "\n".join(DAT.splitlines()[:3])
    assert do_diem_tuan_thu(ba_dong).khoa_xep_hang() > do_diem_tuan_thu(
        DAT.replace("chậm xuống mái", "chậm trên mái")
    ).khoa_xep_hang()


def test_rong_khong_no():
    d = do_diem_tuan_thu("")
    assert not d.tron_ven and d.so_dong == 0


def test_trung_khit_voi_rule_tren_kho_mau():
    """300 bài tuyển đều đạt luật → đều phải trọn vẹn."""
    tap = GOC / "datalake" / "corpus_tuyen" / "tho_mau.jsonl"
    for dong in tap.read_text(encoding="utf-8").splitlines():
        tho = json.loads(dong)["tho"]
        assert kiem_tra_bai_tho(tho).dat
        assert do_diem_tuan_thu(tho).tron_ven, tho
