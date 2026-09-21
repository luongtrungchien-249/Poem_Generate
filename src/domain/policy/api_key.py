"""G13 — vòng đời khoá API: phát hành · hết hạn · thu hồi.

════ LỖ HỔNG ĐANG VÁ ════

Bảng khoá trước đây nạp một lần lúc khởi động, từ biến môi trường. Nghĩa là **thu
hồi một khoá đòi restart**: khi một khoá bị lộ, cửa vẫn mở cho tới lần deploy tiếp
theo. Khoảng thời gian ấy đo bằng giờ hoặc ngày, không phải giây.

════ KHOÁ LƯU DẠNG BĂM, KHÔNG LƯU NGUYÊN VĂN ════

Điều dễ bỏ qua nhất khi chuyển bảng khoá vào cơ sở dữ liệu. Lưu nguyên văn thì một
bản sao lưu rò rỉ là **mọi khoá rò theo** — và sao lưu thì được chép đi khắp nơi,
lên máy lập trình viên, vào kho lưu trữ lạnh, qua email.

Băm thì bản sao lưu vô dụng với kẻ lấy được nó: từ băm không dựng lại được khoá.

Dùng SHA-256 chứ không phải bcrypt/argon2, và đây là lựa chọn có lý do chứ không
phải cẩu thả: khoá API là **chuỗi ngẫu nhiên entropy cao** do hệ thống sinh, không
phải mật khẩu người đặt. Hàm băm chậm tồn tại để chống dò từ điển trên mật khẩu
yếu; với 256 bit ngẫu nhiên thì dò là bất khả bất kể hàm nhanh hay chậm, còn hàm
chậm thì phải trả giá ở MỌI request.

════ FILE NÀY THUẦN ════

Không I/O, không giờ hệ thống lấy ngầm — `bay_gio` truyền vào. Nhờ vậy test kiểm
được ca hết hạn mà không phải chờ hay giả lập đồng hồ.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import Literal, TypeAlias

# 32 byte = 256 bit. Đủ để việc dò là bất khả, và đủ ngắn để copy được.
SO_BYTE_KHOA = 32
TIEN_TO = "sk_"


def sinh_khoa() -> str:
    """Sinh một khoá mới. Giá trị này chỉ hiện MỘT LẦN cho người tạo.

    `secrets` chứ không phải `random`: `random` dùng Mersenne Twister, đoán được
    trạng thái sau khi quan sát đủ đầu ra. Với khoá thì đó là hỏng hoàn toàn.
    """
    return TIEN_TO + secrets.token_urlsafe(SO_BYTE_KHOA)


def bam_khoa(khoa: str) -> str:
    return hashlib.sha256(khoa.encode("utf-8")).hexdigest()


LyDoTuChoi: TypeAlias = Literal["khong_ton_tai", "da_thu_hoi", "da_het_han"]


@dataclass(frozen=True, slots=True)
class BanGhiKhoa:
    """Một khoá đã phát hành. KHÔNG chứa khoá nguyên văn — chỉ băm."""

    bam: str
    tenant_id: str
    ten: str = ""
    tao_luc: float = 0.0
    het_han_luc: float | None = None  # None = không hết hạn
    thu_hoi_luc: float | None = None  # None = còn hiệu lực


@dataclass(frozen=True, slots=True)
class KhoaHopLe:
    tenant_id: str
    ten: str


@dataclass(frozen=True, slots=True)
class KhoaKhongHopLe:
    ly_do: LyDoTuChoi


KetQuaKiemKhoa: TypeAlias = KhoaHopLe | KhoaKhongHopLe


def kiem_khoa(ban_ghi: BanGhiKhoa | None, *, bay_gio: float) -> KetQuaKiemKhoa:
    """Khoá này có dùng được lúc `bay_gio` không.

    THỨ TỰ KIỂM có ý nghĩa: thu hồi trước hết hạn. Một khoá đã thu hồi rồi mới hết
    hạn vẫn phải báo là *đã thu hồi* — đó là thông tin người vận hành cần khi truy
    vết, và hai lý do dẫn tới hai hành động khác nhau.

    ⚠️ `ly_do` là để GHI LOG, KHÔNG để trả cho người gọi. Nói với người gọi rằng
    khoá của họ "đã hết hạn" thay vì "không hợp lệ" là xác nhận khoá ấy từng tồn
    tại — một nửa thông tin cho người đang dò.
    """
    if ban_ghi is None:
        return KhoaKhongHopLe("khong_ton_tai")
    if ban_ghi.thu_hoi_luc is not None and ban_ghi.thu_hoi_luc <= bay_gio:
        return KhoaKhongHopLe("da_thu_hoi")
    if ban_ghi.het_han_luc is not None and ban_ghi.het_han_luc <= bay_gio:
        return KhoaKhongHopLe("da_het_han")
    return KhoaHopLe(tenant_id=ban_ghi.tenant_id, ten=ban_ghi.ten)
