"""Cổng thông tin đầy đủ (chỉ thị 5) và kế hoạch sáng tác.

Bốn ca hỏi lại của §8.2 + QĐ-D5, cộng ca 0 (trường suy đoán).
"""

from __future__ import annotations

import pytest

from application.poetry.plan import KhoPlan, PoetryPlan, kiem_tra_ke_hoach
from application.poetry.requirement import (
    CanHoi,
    DuThongTin,
    PoetryRequirement,
    danh_gia_du_thong_tin,
    mac_dinh,
    nguoi_dung,
    suy_doan,
)

pytestmark = pytest.mark.unit


def _du() -> PoetryRequirement:
    return PoetryRequirement(
        chu_de=nguoi_dung("quê hương"),
        so_dong=nguoi_dung(8),
        cam_xuc=nguoi_dung("hoài niệm"),
        phong_cach=mac_dinh("mộc mạc"),
        rang_buoc_van=mac_dinh("vần chân tự nhiên"),
        rang_buoc_thanh=mac_dinh("khuôn luân phiên"),
        van_ban_goc="Viết bài thất ngôn tự do về quê hương, 8 dòng, giọng hoài niệm.",
    )


# ── Ca thuận ──────────────────────────────────────────────────────────────────


def test_yeu_cau_du_thong_tin_thi_qua_cong():
    kq = danh_gia_du_thong_tin(_du())
    assert isinstance(kq, DuThongTin)
    assert "quê hương" in kq.bang_chung
    assert "4 × 2" in kq.bang_chung


# ── Ca 0 — trường suy đoán ────────────────────────────────────────────────────


def test_truong_suy_doan_KHONG_bao_gio_qua_cong():
    """§3.2: cấm tự suy đoán. Một trường có giá trị nhưng do máy đoán còn nguy hiểm
    hơn trường trống, vì nó trông như đã có thông tin."""
    req = PoetryRequirement(
        chu_de=suy_doan("mùa thu"),
        so_dong=nguoi_dung(8),
        cam_xuc=nguoi_dung("buồn"),
        phong_cach=mac_dinh("x"),
        rang_buoc_van=mac_dinh("y"),
        rang_buoc_thanh=mac_dinh("z"),
    )
    kq = danh_gia_du_thong_tin(req)
    assert isinstance(kq, CanHoi)
    assert kq.ca == 0
    assert "chu_de" in kq.truong_thieu


# ── Ca 1 → 4 của §8.2 và QĐ-D5 ────────────────────────────────────────────────


def test_ca1_thieu_chu_de_thi_hoi_lai():
    kq = danh_gia_du_thong_tin(PoetryRequirement(van_ban_goc="Viết cho tôi một bài thơ."))
    assert isinstance(kq, CanHoi)
    assert kq.ca == 1
    assert "chủ đề" in kq.cau_hoi


def test_ca2_mau_thuan_the_loai_thi_hoi_lai():
    req = PoetryRequirement(
        chu_de=nguoi_dung("mùa thu"),
        so_dong=nguoi_dung(8),
        cam_xuc=nguoi_dung("buồn"),
        phong_cach=mac_dinh("x"),
        rang_buoc_van=mac_dinh("y"),
        rang_buoc_thanh=mac_dinh("z"),
        van_ban_goc="Thơ thất ngôn tự do nhưng bắt buộc đủ luật bằng-trắc của thất ngôn bát cú.",
    )
    kq = danh_gia_du_thong_tin(req)
    assert isinstance(kq, CanHoi)
    assert kq.ca == 2


def test_ca3_rang_buoc_van_mo_ho_thi_hoi_lai():
    req = PoetryRequirement(
        chu_de=nguoi_dung("biển"),
        so_dong=nguoi_dung(8),
        cam_xuc=nguoi_dung("nhớ"),
        phong_cach=mac_dinh("x"),
        rang_buoc_van=mac_dinh(None),
        rang_buoc_thanh=mac_dinh("z"),
        van_ban_goc="Làm bài về biển, vần phải thật chặt.",
    )
    kq = danh_gia_du_thong_tin(req)
    assert isinstance(kq, CanHoi)
    assert kq.ca == 3


@pytest.mark.parametrize("n", [1, 2, 3, 5, 6, 7, 9, 10, 15])
def test_ca4_so_dong_khong_boi_4_thi_hoi_lai(n: int):
    """QĐ-D5. H4 là luật cứng — không được im lặng làm 8 dòng."""
    req = PoetryRequirement(
        chu_de=nguoi_dung("quê"), so_dong=nguoi_dung(n), cam_xuc=nguoi_dung("vui"),
        phong_cach=mac_dinh("x"), rang_buoc_van=mac_dinh("y"), rang_buoc_thanh=mac_dinh("z"),
    )
    kq = danh_gia_du_thong_tin(req)
    assert isinstance(kq, CanHoi)
    assert kq.ca == 4
    assert "bội của 4" in kq.cau_hoi


@pytest.mark.parametrize("n", [4, 8, 12, 16, 100])
def test_so_dong_boi_4_thi_qua(n: int):
    req = PoetryRequirement(
        chu_de=nguoi_dung("quê"), so_dong=nguoi_dung(n), cam_xuc=nguoi_dung("vui"),
        phong_cach=mac_dinh("x"), rang_buoc_van=mac_dinh("y"), rang_buoc_thanh=mac_dinh("z"),
    )
    assert isinstance(danh_gia_du_thong_tin(req), DuThongTin)


def test_cong_KHONG_bao_gio_tu_dien_gia_tri():
    """Cổng chỉ phán đủ/chưa đủ. Nó không được phép sửa yêu cầu."""
    req = PoetryRequirement(van_ban_goc="Viết một bài thơ.")
    danh_gia_du_thong_tin(req)
    assert req.chu_de.gia_tri is None
    assert req.so_dong.gia_tri is None


# ── Kế hoạch ──────────────────────────────────────────────────────────────────


def test_ke_hoach_tong_dong_phai_boi_4():
    plan = PoetryPlan(kho=(KhoPlan(so_dong=3), KhoPlan(so_dong=3)))
    loi = kiem_tra_ke_hoach(plan)
    assert any(e.ma == "K3" for e in loi)


def test_ke_hoach_phai_khop_so_dong_nguoi_dung_xin():
    plan = PoetryPlan(kho=(KhoPlan(so_dong=4),))
    loi = kiem_tra_ke_hoach(plan, so_dong_yeu_cau=8)
    assert any(e.ma == "K4" for e in loi)


def test_ke_hoach_khong_duoc_khai_khuon_pha():
    """QĐ-2 không cho phá khuôn, nên 'pha' không phải lựa chọn hoạch định được."""
    plan = PoetryPlan(kho=(KhoPlan(so_dong=4, khuon="pha"),))  # type: ignore[arg-type]
    loi = kiem_tra_ke_hoach(plan)
    assert any(e.ma == "K5" for e in loi)


def test_ke_hoach_nhip_phai_thuoc_bay_kieu():
    plan = PoetryPlan(kho=(KhoPlan(so_dong=4, nhip="6/1"),))
    loi = kiem_tra_ke_hoach(plan)
    assert any(e.ma == "K5" for e in loi)

    tot = PoetryPlan(kho=(KhoPlan(so_dong=4, nhip="4/3"),))
    assert not kiem_tra_ke_hoach(tot)


def test_ke_hoach_hop_le_thi_khong_loi():
    plan = PoetryPlan(
        muc_tieu="quê hương",
        kho=(KhoPlan(so_dong=4, khuon="bang", nhip="4/3"), KhoPlan(so_dong=4, khuon="trac")),
    )
    assert not kiem_tra_ke_hoach(plan, so_dong_yeu_cau=8)


# ── Ca 5 — thiếu số dòng thì hỏi lại (chủ dự án, 21/09/2026) ──────────────────


def test_ca5_khong_noi_so_dong_thi_hoi_lai():
    """*"Nếu người dùng không yêu cầu số dòng thì hỏi lại số dòng."*

    Số dòng quyết định bài thơ ra sao — bài 4 dòng và bài 16 dòng là hai tác phẩm
    khác hẳn nhau, không phải hai biến thể. Tự chọn hộ là quyết định thay tác giả.
    """
    req = PoetryRequirement(
        chu_de=nguoi_dung("quê hương"),
        cam_xuc=nguoi_dung("nhớ"),
        phong_cach=mac_dinh("x"),
        rang_buoc_van=mac_dinh("y"),
        rang_buoc_thanh=mac_dinh("z"),
        van_ban_goc="Viết bài thơ về quê hương.",
    )
    kq = danh_gia_du_thong_tin(req)
    assert isinstance(kq, CanHoi)
    assert kq.ca == 5
    assert "so_dong" in kq.truong_thieu


def test_ca5_cau_hoi_phai_noi_ca_HAI_ve_cua_luat():
    """F5 + H4 đã hợp nhất: không giới hạn về LƯỢNG, nhưng ràng buộc HÌNH DẠNG.

    Hỏi cụt "bao nhiêu dòng?" thì người dùng trả lời 6 rồi phải hỏi lại ở ca 4.
    Hỏi cụt "4 hay 8?" thì bịa ra một giới hạn mà luật không có.
    """
    kq = danh_gia_du_thong_tin(
        PoetryRequirement(chu_de=nguoi_dung("biển"), van_ban_goc="Viết về biển")
    )
    assert isinstance(kq, CanHoi)
    assert kq.ca == 5
    # vế LƯỢNG: không giới hạn
    assert "bao nhiêu dòng cũng được" in kq.cau_hoi.lower()
    # vế HÌNH DẠNG: bội của 4
    assert "bội của 4" in kq.cau_hoi
    # và nêu ví dụ mở, không phải một danh sách đóng
    assert "16" in kq.cau_hoi and "…" in kq.cau_hoi


def test_ca5_KHONG_tu_dien_so_dong():
    req = PoetryRequirement(chu_de=nguoi_dung("biển"), van_ban_goc="Viết về biển")
    danh_gia_du_thong_tin(req)
    assert req.so_dong.gia_tri is None, "cổng không được tự điền số dòng"


def test_ca1_uu_tien_hon_ca5_khi_thieu_ca_hai():
    """Thiếu cả chủ đề lẫn số dòng thì hỏi chủ đề trước — đúng thứ tự §8.2."""
    kq = danh_gia_du_thong_tin(PoetryRequirement(van_ban_goc="Viết một bài thơ."))
    assert isinstance(kq, CanHoi)
    assert kq.ca == 1
