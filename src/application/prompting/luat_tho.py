"""VỎ TƯƠNG THÍCH — bảng luật nay định nghĩa ở `prompting/system.py`.

════ VÌ SAO FILE NÀY CHỈ CÒN LÀ MỘT VỎ, 23/09/2026 ════

Chủ dự án chốt: *"Thay vì import vào trong system.py, tôi cần bạn thêm trực tiếp
BANG_LUAT_THO + CACH_VIET_DUNG_LUAT vào trong system.py"*.

Hai khối ấy nay nằm nguyên trong `system.py`. File này giữ lại vì đường
`/v1/poem` và bảy test đang đọc qua đây — gỡ luôn là bắt sửa tám chỗ cho một
việc không đổi hành vi gì.

⛔ ĐỪNG ĐỊNH NGHĨA LẠI Ở ĐÂY. Lý do không phải gọn mắt, mà là một lỗi đã xảy ra
thật trong chính ngày này: bảng luật từng tồn tại SONG SONG ở `poetry/prompt.py`
và ở đây, rồi trôi thành 1.436 vs 1.938 ký tự — hai đường sinh thơ được dạy hai
phần nhịp khác nhau, không lỗi, không cảnh báo.

`test_CHI_MOT_bang_luat_cho_ca_hai_duong` ghim bằng `is`, không phải `==`: hai
chuỗi bằng nhau hôm nay vẫn tách ra được ngày mai.

Chiều phụ thuộc: file này -> `system.py` -> `rule.py`. Không có vòng lặp, vì
`system.py` KHÔNG import ngược lại đây.
"""

from __future__ import annotations

from application.prompting.system import (
    BANG_LUAT_THO,
    CACH_VIET_DUNG_LUAT,
    HIEU_QUA_NHIP,
)

__all__ = ["BANG_LUAT_THO", "CACH_VIET_DUNG_LUAT", "HIEU_QUA_NHIP"]
