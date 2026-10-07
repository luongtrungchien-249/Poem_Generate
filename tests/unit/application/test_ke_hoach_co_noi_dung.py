"""QĐ-KH-1 phương án B — kế hoạch phải mang được nội dung của người dùng.

🩸 TRƯỚC 21/09/2026: `PoetryPlan` có `mach_cam_xuc` và `hinh_anh`, `planner.py` nói
rõ đó là "phần mô hình LÀM TỐT HƠN", và **không ai truyền vào**. Đường sinh thơ gọi
`lap_ke_hoach_hop_le(yeu_cau)` — hàm chỉ nhận `req`. Nên hai trường luôn rỗng, và
nhánh `if plan.hinh_anh:` trong `mo_ta_ke_hoach_cho_mo_hinh` chưa bao giờ chạy.

Cùng loại hỏng với `KHUON_TRONG_CHI_DAN`: ô trống khai báo tử tế, không đường nào
dẫn tới. Test dưới đây ghim đường dẫn đó, không ghim câu chữ.
"""

from __future__ import annotations

from application.poetry.planner import lap_ke_hoach_hop_le, mo_ta_ke_hoach_cho_mo_hinh
from application.poetry.requirement import PoetryRequirement, Truong


def _yeu_cau(cam_xuc: str | None = None) -> PoetryRequirement:
    return PoetryRequirement(
        chu_de=Truong(gia_tri="mùa thu", nguon="nguoi_dung"),
        so_dong=Truong(gia_tri=8, nguon="nguoi_dung"),
        cam_xuc=(
            Truong(gia_tri=cam_xuc, nguon="nguoi_dung")
            if cam_xuc
            else PoetryRequirement().cam_xuc
        ),
    )


def test_cam_xuc_nguoi_dung_DI_TOI_ke_hoach():
    """Ca hỏng cũ: người dùng nêu cảm xúc, kế hoạch không mang theo gì."""
    plan = lap_ke_hoach_hop_le(_yeu_cau("tiếc nuối một mùa đã qua"))
    assert plan is not None
    assert plan.mach_cam_xuc == ("tiếc nuối một mùa đã qua",)


def test_cam_xuc_DI_TIEP_toi_chuoi_gui_mo_hinh():
    """Vào được `PoetryPlan` chưa đủ — phải ra tới chuỗi thật gửi đi."""
    plan = lap_ke_hoach_hop_le(_yeu_cau("tiếc nuối một mùa đã qua"))
    assert "tiếc nuối một mùa đã qua" in mo_ta_ke_hoach_cho_mo_hinh(plan)


def test_khong_neu_cam_xuc_thi_KHONG_bia_ra():
    """Thiếu thông tin thì để trống, không chọn hộ — cùng nguyên tắc với cổng B1."""
    plan = lap_ke_hoach_hop_le(_yeu_cau())
    assert plan is not None
    assert plan.mach_cam_xuc == ()


def test_mot_cam_xuc_KHONG_bi_chia_deu_cho_moi_kho():
    """Người dùng nêu MỘT cảm xúc thì đó là một, không phải n cái chia đều.

    Bịa thêm ý cho các khổ sau là quyết định thay tác giả.
    """
    plan = lap_ke_hoach_hop_le(_yeu_cau("tiếc nuối"))
    assert len(plan.kho) == 2
    assert plan.kho[0].y_chinh == "tiếc nuối"
    assert plan.kho[1].y_chinh == ""


# ══════════════════════════════════════════════════════════════════════════════
# LẬP LẠI KẾ HOẠCH — 22/09/2026
#
# Nấc cuối của thang bảo "viết lại toàn bài", nhưng kế hoạch thì không đổi — mô
# hình được bảo dựng lại theo đúng bản vẽ vừa dẫn nó tới chỗ hỏng.
#
# Bản này TẤT ĐỊNH và chỉ đổi phần suy ra được. Nó KHÔNG phải replanner của
# `compare_prompt.py` (bản cũ để LLM nghĩ lại nội dung) — xem chú thích ở
# `planner.lap_lai_ke_hoach`.
# ══════════════════════════════════════════════════════════════════════════════

from dataclasses import replace  # noqa: E402

from application.poetry.planner import (  # noqa: E402
    NHIP_THAY_THE,
    lap_lai_ke_hoach,
)


def _plan(so_dong=8, cam_xuc="nhớ nhà"):
    """Dựng qua `lap_ke_hoach_hop_le` — ĐÚNG đường mà đường sinh thơ đi.

    `lap_ke_hoach` trần không suy `mach_cam_xuc` từ yêu cầu (nó nhận qua kwarg),
    nên dùng nó ở đây sẽ test một kế hoạch không bao giờ tồn tại trong thực tế.
    """
    req = _yeu_cau(cam_xuc)
    if so_dong != 8:
        req = replace(req, so_dong=Truong(gia_tri=so_dong, nguon="nguoi_dung"))
    plan = lap_ke_hoach_hop_le(req)
    assert plan is not None
    return plan


def test_loi_thanh_luat_thi_DAO_PHA_khuon():
    """Mô hình hỏng thanh luật liên tục -> rất có thể nó vật lộn với đúng khuôn
    được gợi ý cho khổ đầu. Đảo lại cho nó một xuất phát khác."""
    cu = _plan()
    moi = lap_lai_ke_hoach(cu, ["S2", "S2"])
    assert [k.khuon for k in cu.kho] == ["bang", "trac"]
    assert [k.khuon for k in moi.kho] == ["trac", "bang"]


def test_dao_pha_VAN_GIU_tinh_luan_phien():
    """S2 nói "nên luân phiên bằng – trắc". Đảo pha giữ nguyên tinh thần đó."""
    moi = lap_lai_ke_hoach(_plan(so_dong=16), ["S2"])
    khuon = [k.khuon for k in moi.kho]
    assert all(a != b for a, b in zip(khuon, khuon[1:], strict=False))


def test_loi_nhip_thi_doi_sang_kieu_THAY_THE():
    moi = lap_lai_ke_hoach(_plan(), ["S14"])
    assert {k.nhip for k in moi.kho} == {NHIP_THAY_THE}


def test_KHONG_co_bang_chung_thi_KHONG_doi_gi():
    """⛔ Đổi bừa một kế hoạch vốn không sai là làm hỏng thứ đang đúng, và làm mất
    luôn manh mối vì sao bài trượt."""
    cu = _plan()
    assert lap_lai_ke_hoach(cu, ["H1", "H4", "CL3"]) == cu
    assert lap_lai_ke_hoach(cu, []) == cu


def test_KHONG_dung_toi_noi_dung_cua_nguoi_dung():
    """🔴 `mach_cam_xuc` đến từ yêu cầu người dùng. Đổi nó là quyết định thay tác
    giả — cùng lý do cổng B1 không tự chọn hộ số dòng."""
    cu = _plan(cam_xuc="nhớ nhà")
    moi = lap_lai_ke_hoach(cu, ["S2", "S14"])
    assert moi.mach_cam_xuc == cu.mach_cam_xuc == ("nhớ nhà",)
    assert moi.muc_tieu == cu.muc_tieu
    assert moi.chien_luoc_van == cu.chien_luoc_van
    assert moi.tong_so_dong == cu.tong_so_dong


def test_VAN_TAT_DINH():
    """Planner tất định là bất biến của module. Lập lại cũng phải vậy."""
    cu = _plan()
    assert lap_lai_ke_hoach(cu, ["S2"]) == lap_lai_ke_hoach(cu, ["S2"])


def test_ke_hoach_moi_VAN_HOP_LE():
    """Đổi xong mà vi phạm H4 hay QĐ-2 thì bước B3 sẽ chặn oan mọi bản nháp."""
    from application.poetry.plan import kiem_tra_ke_hoach

    moi = lap_lai_ke_hoach(_plan(so_dong=8), ["S2", "S14"])
    assert kiem_tra_ke_hoach(moi, 8) == ()
