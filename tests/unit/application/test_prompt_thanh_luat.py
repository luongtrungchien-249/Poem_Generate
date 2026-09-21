"""Prompt dạy thanh luật phải nói ĐÚNG thứ bộ luật dùng để chấm.

Lệch giữa hai thứ đó là kiểu hỏng tệ nhất của hệ thống này: mô hình được dạy một
khuôn, rồi bị đánh trượt bằng một khuôn khác, và không ai nhìn ra vì cả hai phía
đều "chạy đúng".
"""

from __future__ import annotations

import pytest

from application.poetry.fewshot import _bang_khuon, dung_khoi_vi_du
from application.poetry.prompt import CHI_DAN_SINH_THO
from application.rule import khuon_cua_dong, kiem_tra_bai_tho, tach_tieng

BAI_DUNG_LUAT = """Nắng vàng rực rỡ sớm mai về,
Quê hương lúa chín ngát hương quê.
Dòng sông trong vắt gợi niềm nhớ,
Hình bóng tuổi thơ mãi vẫn nề."""


# ── Chú thích khuôn phải khớp phán quyết của rule.py ─────────────────────────


def test_bai_mau_dung_la_dung_luat():
    """Kiểm soát dương: nếu bài mẫu này không còn đúng luật thì các phép kiểm
    dưới đây không nói lên điều gì."""
    assert kiem_tra_bai_tho(BAI_DUNG_LUAT).dat


def test_chu_thich_khop_voi_phan_quyet_cua_rule():
    bang = _bang_khuon(BAI_DUNG_LUAT)
    dong_tho = [d for d in BAI_DUNG_LUAT.splitlines() if d.strip()]
    hang = bang.splitlines()
    assert len(hang) == len(dong_tho)

    for h, d in zip(hang, dong_tho, strict=True):
        khuon = khuon_cua_dong(tach_tieng(d))
        # Nhãn trong prompt phải là nhãn mà rule.py gán cho chính dòng đó.
        assert ("khuôn bằng" in h) == (khuon == "bang"), h
        assert ("khuôn trắc" in h) == (khuon == "trac"), h


def test_chu_thich_neu_dung_tieng_2_4_6():
    """Chú thích sai vị trí còn tệ hơn không có: nó dạy mô hình soát nhầm chỗ."""
    dong = "Nắng vàng rực rỡ sớm mai về,"
    tieng = tach_tieng(dong)
    h = _bang_khuon(dong)
    assert f"{tieng[1]}=" in h and f"{tieng[3]}=" in h and f"{tieng[5]}=" in h
    # Và KHÔNG nêu các vị trí luật không đụng tới.
    for i in (0, 2, 4, 6):
        assert f"{tieng[i]}=" not in h or tieng[i] in (tieng[1], tieng[3], tieng[5])


def test_dong_khong_du_tieng_thi_BO_QUA_khong_doan_bua():
    """Dòng thiếu tiếng thì P2/P4/P6 không còn là P2/P4/P6 của thể — `rule.py` trả
    "khong_xac_dinh", và prompt không được tự gán cho nó một khuôn."""
    assert _bang_khuon("Trời xanh quá") == ""


# ── Ví dụ không được dạy mô hình viết chú thích vào bài ──────────────────────


@pytest.mark.parametrize(
    "canh_bao", ["CHỈ GỒM CÁC DÒNG THƠ", "không kèm chú thích", "không đánh dấu B/T"]
)
def test_khoi_vi_du_canh_bao_khong_chep_chu_thich(canh_bao):
    """⛔ Bộ đọc ứng viên chỉ lấy BỐN DÒNG ĐẦU không rỗng.

    Nếu mô hình bắt chước ví dụ và viết bảng khuôn vào bài của nó, dòng chú thích
    lọt vào bốn dòng đầu và cả ứng viên hỏng — dù bài thơ có thể đúng luật.
    """
    from application.poetry.dataset import MauTho
    from application.poetry.fewshot import ViDuDuocChon

    mau = MauTho(
        id="thu", tieu_de="thử", tho=BAI_DUNG_LUAT, so_dong=4, so_kho=1,
        so_do_van=("aaxa",), phoi_khuon=("co_dien",), tu_khoa=frozenset({"quê"}),
    )
    khoi = dung_khoi_vi_du([ViDuDuocChon(mau=mau, diem=1, ly_do=("thử",))])
    assert canh_bao in khoi


def test_khoi_vi_du_rong_khi_khong_co_mau():
    assert dung_khoi_vi_du([]) == ""


# ── Chỉ dẫn phải nói được cách TRA, không chỉ nói tên thanh ──────────────────


def test_chi_dan_co_bang_tra_DAU_sang_thanh():
    """Nói "B = bằng (ngang, huyền)" là nêu tên loại thanh, không phải cách nhận ra
    nó. Mô hình cần bảng tra từ DẤU — thứ nó nhìn thấy trên mặt chữ."""
    for dau in ("dấu huyền", "dấu sắc", "dấu hỏi", "dấu ngã", "dấu nặng"):
        assert dau in CHI_DAN_SINH_THO, dau
    assert "không dấu" in CHI_DAN_SINH_THO


def test_chi_dan_neu_ro_chi_xet_tieng_2_4_6():
    assert "tiếng thứ 2, 4, 6" in CHI_DAN_SINH_THO
    # Và nói rõ các vị trí còn lại là TỰ DO — thiếu vế này thì mô hình tự trói
    # mình thêm ràng buộc không có thật, làm hẹp không gian tìm câu.
    assert "1, 3, 5, 7" in CHI_DAN_SINH_THO


def test_chi_dan_bao_chon_tieng_2_4_6_TRUOC():
    """Thứ tự làm việc là phần dạy được. Viết câu trước rồi sửa thanh thì sửa
    thanh làm gãy nghĩa, sửa nghĩa lại làm lệch thanh."""
    assert "2, 4, 6" in CHI_DAN_SINH_THO
    assert "lấp" in CHI_DAN_SINH_THO


def test_chi_dan_KHONG_bao_mo_hinh_viet_phan_soat_ra_ngoai():
    """Ứng viên chỉ được gồm dòng thơ — xem bộ đọc bốn dòng đầu."""
    assert "ĐỪNG viết phần soát ra ngoài" in CHI_DAN_SINH_THO
