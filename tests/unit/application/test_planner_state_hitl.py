"""G4 (Planner · State Machine) và G7 (HITL · Feedback)."""

from __future__ import annotations

import pytest

from application.poetry.feedback import HangDoiPhanHoi, PhanHoi, duyet_lam_mau
from application.poetry.plan import kiem_tra_ke_hoach
from application.poetry.planner import lap_ke_hoach, lap_ke_hoach_hop_le
from application.poetry.requirement import PoetryRequirement, mac_dinh, nguoi_dung
from application.poetry.state import (
    CHUYEN_HOP_LE,
    ChuyenTrangThaiSai,
    DauVetTrangThai,
)
from application.rule import kiem_tra_bai_tho
from domain.policy.hitl import TinHieuHitl, duoc_tra_thang, quyet_dinh_hitl

pytestmark = pytest.mark.unit

BAI_DUNG = (
    "Chiều rơi chậm xuống mái rêu xanh\n"
    "Gió cuốn heo may lạc cuối ghềnh\n"
    "Một bóng con đò trôi lặng lẽ\n"
    "Sông dài ôm trọn mảnh trời xanh"
)
BAI_SAI = "\n".join(["Một dòng sáu tiếng thôi mà"] * 4)


def _req(n: int | None = 8) -> PoetryRequirement:
    return PoetryRequirement(
        chu_de=nguoi_dung("quê hương"),
        so_dong=nguoi_dung(n) if n else mac_dinh(None),
        cam_xuc=mac_dinh(None), phong_cach=mac_dinh(None),
        rang_buoc_van=mac_dinh(None), rang_buoc_thanh=mac_dinh(None),
    )


# ── G4 Planner ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize("n", [4, 8, 12, 16, 100])
def test_ke_hoach_luon_hop_le_voi_so_dong_boi_4(n: int):
    plan = lap_ke_hoach(_req(n))
    assert plan.tong_so_dong == n
    assert not kiem_tra_ke_hoach(plan, n)


def test_ke_hoach_chia_4_dong_moi_kho_theo_S17():
    plan = lap_ke_hoach(_req(12))
    assert len(plan.kho) == 3
    assert all(k.so_dong == 4 for k in plan.kho)


def test_ke_hoach_luan_phien_khuon_theo_tinh_than_S2():
    plan = lap_ke_hoach(_req(16))
    assert [k.khuon for k in plan.kho] == ["bang", "trac", "bang", "trac"]


def test_ke_hoach_KHONG_lam_tron_yeu_cau_sai():
    """Kế hoạch phải phản ánh đúng yêu cầu, kể cả khi yêu cầu sai — rồi để K3 báo.

    Lặng lẽ làm tròn 6 thành 8 là sửa yêu cầu của người dùng sau lưng họ.
    """
    plan = lap_ke_hoach(_req(6))
    assert plan.tong_so_dong == 6
    assert any(e.ma == "K3" for e in kiem_tra_ke_hoach(plan, 6))


def test_ke_hoach_hong_thi_tra_None_chu_khong_keo_theo_ke_hoach_sai():
    assert lap_ke_hoach_hop_le(_req(6)) is None
    assert lap_ke_hoach_hop_le(_req(8)) is not None


def test_ke_hoach_TAT_DINH():
    assert lap_ke_hoach(_req(8)) == lap_ke_hoach(_req(8))


# ── G4 State Machine ─────────────────────────────────────────────────────────


def test_duong_di_thuan_hop_le():
    v = DauVetTrangThai()
    for t in (
        "VALIDATED", "ANALYZING", "RESEARCHING", "PLANNING", "GENERATING",
        "VERIFYING", "VERIFIED", "SAFETY_CHECK", "FINAL_RESPONSE", "FEEDBACK", "END",
    ):
        v.chuyen(t)  # type: ignore[arg-type]
    assert v.hien_tai == "END"
    assert v.duong_di()[0] == "RECEIVED"


def test_chuyen_sai_thi_NEM_NGOAI_LE():
    """Lỗi lập trình, không phải tình huống nghiệp vụ -> ngoại lệ, không phải Result."""
    v = DauVetTrangThai()
    with pytest.raises(ChuyenTrangThaiSai):
        v.chuyen("FINAL_RESPONSE")


def test_moi_trang_thai_deu_den_duoc():
    """Trạng thái không ai tới được là trạng thái chết trong một sơ đồ đẹp."""
    tat_ca = set(CHUYEN_HOP_LE)
    den_duoc = {d for ds in CHUYEN_HOP_LE.values() for d in ds} | {"RECEIVED"}
    assert tat_ca == den_duoc, f"lệch: {tat_ca ^ den_duoc}"


def test_lich_su_ghi_lai_ly_do():
    v = DauVetTrangThai()
    v.chuyen("VALIDATED", "qua rào")
    assert v.lich_su[0].ly_do == "qua rào"


# ── G7 HITL ──────────────────────────────────────────────────────────────────


def _th(**kw: object) -> TinHieuHitl:
    goc: dict[str, object] = {
        "yeu_cau_day_du": True, "an_toan_dat": True,
        "dat_luat": True, "dat_chat_luong": True, "so_luot_sua": 0,
    }
    goc.update(kw)
    return TinHieuHitl(**goc)  # type: ignore[arg-type]


def test_moi_thu_dat_thi_tu_tra_loi():
    assert quyet_dinh_hitl(_th()).quyet_dinh == "AUTO_RESPOND"


def test_khong_an_toan_thi_REJECT_bat_ke_moi_thu_khac():
    assert quyet_dinh_hitl(_th(an_toan_dat=False)).quyet_dinh == "REJECT"
    assert quyet_dinh_hitl(_th(an_toan_dat=False, dat_luat=True)).quyet_dinh == "REJECT"


def test_thieu_thong_tin_thi_hoi_NGUOI_DUNG_chu_khong_day_cho_reviewer():
    """Reviewer không biết người dùng muốn gì hơn chính người dùng."""
    assert quyet_dinh_hitl(_th(yeu_cau_day_du=False)).quyet_dinh == "ASK_USER"


def test_sai_luat_thi_REJECT_chu_khong_dua_nguoi_duyet():
    """Bộ kiểm tất định; người xem lại không đổi được phán quyết ấy."""
    assert quyet_dinh_hitl(_th(dat_luat=False)).quyet_dinh == "REJECT"


def test_TIEBREAKER_theo_dinh_nghia_MOI_cua_QD_D3():
    """§22.3 gốc định nghĩa tiebreaker là 'checker A ≠ checker B' — tình huống
    không tồn tại với một nguồn luật tất định. QĐ-D3 định nghĩa lại: hai loại
    bằng chứng KHÁC LOẠI nói ngược nhau."""
    kq = quyet_dinh_hitl(_th(dat_luat=True, dat_chat_luong=False))
    assert kq.quyet_dinh == "HUMAN_TIEBREAKER"
    assert "chất lượng" in kq.ly_do


def test_chu_de_can_xem_lai_thi_HUMAN_REVIEW():
    assert quyet_dinh_hitl(_th(chu_de_can_xem_lai=True)).quyet_dinh == "HUMAN_REVIEW"


def test_cham_tran_luot_sua_thi_HUMAN_REVIEW_chu_khong_chan():
    assert quyet_dinh_hitl(_th(so_luot_sua=3, tran_luot_sua=3)).quyet_dinh == "HUMAN_REVIEW"


def test_chi_AUTO_RESPOND_duoc_tra_thang():
    for q in ("ASK_USER", "HUMAN_REVIEW", "HUMAN_TIEBREAKER", "REJECT"):
        assert not duoc_tra_thang(q)  # type: ignore[arg-type]
    assert duoc_tra_thang("AUTO_RESPOND")


def test_moi_quyet_dinh_deu_co_LY_DO():
    for t in (
        _th(), _th(an_toan_dat=False), _th(yeu_cau_day_du=False),
        _th(dat_luat=False), _th(dat_chat_luong=False), _th(chu_de_can_xem_lai=True),
    ):
        assert quyet_dinh_hitl(t).ly_do


# ── G7 Feedback: cái van giữa lời khen và kho mẫu ────────────────────────────


def _ph(**kw: object) -> PhanHoi:
    goc: dict[str, object] = {
        "trace_id": "t", "yeu_cau": "viết thơ", "bai_tho": BAI_DUNG, "danh_gia": "tot",
    }
    goc.update(kw)
    return PhanHoi(**goc)  # type: ignore[arg-type]


def test_bai_duoc_khen_VA_dung_luat_thi_thanh_mau():
    kq = duyet_lam_mau(_ph())
    assert kq.trang_thai == "da_duyet"
    assert kq.mau == BAI_DUNG


def test_bai_duoc_khen_nhung_SAI_LUAT_thi_BI_TU_CHOI():
    """⛔ Cái van quan trọng nhất của §24.

    Người dùng khen bài vì nó hay, không vì nó đủ 7 tiếng mỗi dòng. Để một lời
    khen tự động thành ví dụ mẫu là phá bất biến của few-shot trong im lặng.
    """
    kq = duyet_lam_mau(_ph(bai_tho=BAI_SAI))
    assert kq.trang_thai == "tu_choi"
    assert "KHÔNG đạt luật" in kq.ly_do
    assert kq.mau == ""


def test_phan_hoi_xau_khong_bao_gio_thanh_mau():
    assert duyet_lam_mau(_ph(danh_gia="xau")).trang_thai == "tu_choi"


def test_uu_tien_ban_nguoi_dung_TU_SUA():
    """Bỏ công viết lại là tín hiệu mạnh hơn một lần bấm nút."""
    kq = duyet_lam_mau(_ph(bai_tho=BAI_SAI, sua_cua_nguoi=BAI_DUNG))
    assert kq.trang_thai == "da_duyet"
    assert kq.mau == BAI_DUNG


def test_sua_qua_nhieu_luot_thi_CHO_NGUOI_DUYET():
    assert duyet_lam_mau(_ph(so_luot_sua=3)).trang_thai == "cho_duyet"


def test_hang_doi_phan_loai_dung_ba_nhanh():
    hd = HangDoiPhanHoi()
    hd.nhan(_ph())
    hd.nhan(_ph(bai_tho=BAI_SAI))
    hd.nhan(_ph(so_luot_sua=5))
    assert len(hd.da_duyet) == 1
    assert len(hd.tu_choi) == 1
    assert len(hd.cho_duyet) == 1


def test_KHONG_co_duong_nao_dua_bai_sai_luat_vao_kho_mau():
    """Tính chất, không phải ca lẻ: quét mọi tổ hợp đầu vào."""
    hd = HangDoiPhanHoi()
    for danh_gia in ("tot", "xau"):
        for bai in (BAI_DUNG, BAI_SAI, ""):
            for sua in ("", BAI_SAI, BAI_DUNG):
                hd.nhan(_ph(danh_gia=danh_gia, bai_tho=bai, sua_cua_nguoi=sua))
    for m in hd.da_duyet:
        assert kiem_tra_bai_tho(m).dat, f"bài sai luật lọt vào kho mẫu: {m[:40]}"
