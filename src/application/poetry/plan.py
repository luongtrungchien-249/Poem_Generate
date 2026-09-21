"""KẾ HOẠCH SÁNG TÁC — §10 tài liệu đích, đã bị QĐ-D1 và QĐ-D5 ghi đè.

HAI CHỖ KHÁC TÀI LIỆU, ghi rõ để không ai khôi phục nhầm:

  1. §10 viết: *"Mỗi dòng hướng tới 7 tiếng, nhưng cho phép biến đổi nếu user không
     yêu cầu ràng buộc cứng."*  ->  **BỎ** (QĐ-D1). H1/H2 là luật cứng, không ngoại
     lệ. Vì vậy `KhoPlan` KHÔNG có trường số tiếng: không có gì để hoạch định ở đó,
     con số 7 là hằng số của thể.

  2. §10 không nhắc H4.  ->  `tong_so_dong` phải là bội của 4 (QĐ-D5), kiểm ngay ở
     kế hoạch chứ không đợi tới lúc kiểm bài.

Kế hoạch sai thì bài viết ra chắc chắn sai. Bắt lỗi ở đây rẻ hơn bắt sau khi đã tốn
một lượt gọi mô hình.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias

# `rule.py` ĐÓNG BĂNG: chỉ đọc hai hằng số.
from application.rule import NHIP_TAI_LIEU, SO_TIENG_MOI_DONG

KhuonKeHoach: TypeAlias = Literal["bang", "trac"]

# QĐ-2 không cho phá khuôn, nên kế hoạch chỉ được khai hai khuôn này. "pha" và
# "khong_xac_dinh" của `rule.Khuon` là KẾT QUẢ ĐO, không phải lựa chọn hoạch định
# được — cố ý không nhận ở đây.
KHUON_HOP_LE: frozenset[str] = frozenset({"bang", "trac"})


@dataclass(frozen=True, slots=True)
class KhoPlan:
    """Một khổ trong kế hoạch."""

    so_dong: int
    y_chinh: str = ""
    khuon: KhuonKeHoach | None = None  # None = để mô hình tự chọn, vẫn phải khớp một khuôn
    nhip: str | None = None  # một trong bảy kiểu của NHIP_TAI_LIEU


@dataclass(frozen=True, slots=True)
class LoiKeHoach:
    ma: str
    cho: str
    ky_vong: str
    thuc_te: str


@dataclass(frozen=True, slots=True)
class PoetryPlan:
    """§10 `PoetryPlan`, bỏ hai trường không kiểm được và thêm ràng buộc H4."""

    muc_tieu: str = ""
    mach_cam_xuc: tuple[str, ...] = ()
    kho: tuple[KhoPlan, ...] = ()
    chien_luoc_van: str = ""
    chien_luoc_thanh: str = ""
    hinh_anh: tuple[str, ...] = field(default_factory=tuple)

    @property
    def tong_so_dong(self) -> int:
        return sum(k.so_dong for k in self.kho)


def kiem_tra_ke_hoach(
    plan: PoetryPlan, so_dong_yeu_cau: int | None = None
) -> tuple[LoiKeHoach, ...]:
    """Kiểm kế hoạch trước khi cho Writer chạy. Rỗng = hợp lệ.

    Năm phép kiểm, tất cả đều suy ra từ luật đã có, không phép nào tự chế:

        K1  phải có ít nhất một khổ           — không có khổ thì không có bài
        K2  mỗi khổ phải có số dòng dương
        K3  tổng số dòng là bội của 4          — H4
        K4  tổng số dòng khớp yêu cầu người dùng, nếu có
        K5  khuôn và nhịp khai báo phải hợp lệ — QĐ-2 và QĐ-6
    """
    loi: list[LoiKeHoach] = []

    if not plan.kho:
        loi.append(
            LoiKeHoach(
                ma="K1", cho="toàn kế hoạch",
                ky_vong="ít nhất một khổ", thuc_te="không có khổ nào",
            )
        )

    for i, k in enumerate(plan.kho, start=1):
        if k.so_dong <= 0:
            loi.append(
                LoiKeHoach(
                    ma="K2", cho=f"khổ {i}",
                    ky_vong="số dòng dương", thuc_te=f"{k.so_dong} dòng",
                )
            )
        if k.khuon is not None and k.khuon not in KHUON_HOP_LE:
            loi.append(
                LoiKeHoach(
                    ma="K5", cho=f"khổ {i}",
                    ky_vong="khuôn thuộc {bang, trac} — QĐ-2 không cho phá khuôn",
                    thuc_te=f"khuôn {k.khuon!r}",
                )
            )
        if k.nhip is not None and k.nhip not in NHIP_TAI_LIEU:
            loi.append(
                LoiKeHoach(
                    ma="K5", cho=f"khổ {i}",
                    ky_vong=f"nhịp thuộc bảy kiểu {sorted(NHIP_TAI_LIEU)}",
                    thuc_te=f"nhịp {k.nhip!r}",
                )
            )

    tong = plan.tong_so_dong
    if plan.kho and tong % 4 != 0:
        loi.append(
            LoiKeHoach(
                ma="K3", cho="toàn kế hoạch",
                ky_vong="tổng số dòng là bội của 4 (H4, luật cứng)",
                thuc_te=f"{tong} dòng, dư {tong % 4}",
            )
        )

    if so_dong_yeu_cau is not None and plan.kho and tong != so_dong_yeu_cau:
        loi.append(
            LoiKeHoach(
                ma="K4", cho="toàn kế hoạch",
                ky_vong=f"{so_dong_yeu_cau} dòng (người dùng yêu cầu)",
                thuc_te=f"kế hoạch {tong} dòng",
            )
        )

    return tuple(loi)


def mo_ta_ke_hoach(plan: PoetryPlan) -> str:
    """Một dòng người đọc kiểm lại được bằng mắt."""
    if not plan.kho:
        return "kế hoạch rỗng"
    kich_thuoc = " + ".join(str(k.so_dong) for k in plan.kho)
    return (
        f"{len(plan.kho)} khổ ({kich_thuoc} = {plan.tong_so_dong} dòng), "
        f"mỗi dòng {SO_TIENG_MOI_DONG} tiếng"
    )
