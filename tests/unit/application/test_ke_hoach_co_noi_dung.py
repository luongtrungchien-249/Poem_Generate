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
