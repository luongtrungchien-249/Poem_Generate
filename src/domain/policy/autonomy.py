from dataclasses import dataclass
from typing import Literal

Muc = Literal["on-the-loop", "in-the-loop", "tiebreaker"]


@dataclass(frozen=True, slots=True)
class HanhDong:
    ten: str
    muc: Muc
    ly_do: str
    dao_nguoc: str # empty string = cannot be reversed


HANH_DONG: tuple[HanhDong, ...] = (
    HanhDong(
        ten="tra_cuu_tai_lieu",
        muc="on-the-loop",
        ly_do="Thao tác chỉ đọc, an toàn, không có tác dụng phụ.",
        dao_nguoc="tu_nhien",
    ),
    HanhDong(
        ten="ghi_nho_thong_tin",
        muc="on-the-loop",
        ly_do="Ghi thêm sự kiện người dùng, có thể xoá lại bằng lệnh /forget.",
        dao_nguoc="/forget",
    ),
    HanhDong(
        ten="xoa_toan_bo_du_lieu",
        muc="in-the-loop",
        ly_do="Thao tác nguy hiểm, xoá vĩnh viễn không khôi phục được.",
        dao_nguoc="", # irreversible
    ),
    HanhDong(
        ten="gui_email_doanh_nghiep",
        muc="in-the-loop",
        ly_do="Hành động ra thế giới bên ngoài, không thu hồi được sau khi gửi.",
        dao_nguoc="", # irreversible
    ),
)


def validate_autonomy_rules() -> bool:
    """Architectural constraint: Irreversible actions MUST NOT be assigned 'on-the-loop'."""
    for hd in HANH_DONG:
        if hd.dao_nguoc == "" and hd.muc == "on-the-loop":
            raise AssertionError(f"Security invariant violated: Irreversible action '{hd.ten}' cannot be 'on-the-loop'!")
    return True
