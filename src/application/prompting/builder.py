"""Bọc nội dung không tin cậy vào thẻ ranh giới.

════ VẤN ĐỀ THẺ RANH GIỚI ════

Hệ thống dùng thẻ XML để nói với mô hình "phần này là dữ liệu, không phải lệnh":

    <tai_lieu>
    …văn bản lấy từ kho…
    </tai_lieu>

Ranh giới ấy chỉ có giá trị khi nội dung bên trong KHÔNG tự đóng thẻ được. Người
dùng viết `</tai_lieu>` giữa văn bản của mình là thoát ra ngoài vùng dữ liệu, và
mọi chữ sau đó được mô hình đọc như chỉ dẫn ngang hàng với chỉ dẫn hệ thống.

════ VÌ SAO KHÔNG DÙNG DANH SÁCH CỐ ĐỊNH ════

🔴 ĐÃ VÁ 21/09/2026. Bản trước lọc theo một danh sách gõ tay:

    tai_lieu | context | tool_result | fact | prompt

Trong khi hệ thống thật sự dùng CHÍN thẻ ranh giới: `bien_ban_kiem_dinh`,
`chi_dan_tu_nguoi_dung`, `ke_hoach_bat_buoc`, `tai_lieu`, `thong_tin_nguoi_dung`,
`phan_da_viet`, `tom_tat`, `vi_du_dung_luat`, `yeu_cau_bai_tho`. Chỉ MỘT trong
chín được bảo vệ;
bốn tên còn lại trong danh sách thậm chí không được dùng ở đâu.

Nghĩa là tám vùng dữ liệu thoát ra được — kể cả `yeu_cau_bai_tho`, nơi chứa đúng
văn bản do người dùng gõ vào.

Một danh sách phải giữ đồng bộ bằng trí nhớ thì chắc chắn sẽ lệch. Nên thiết kế
ở đây đổi hướng: **bọc bằng thẻ nào thì thẻ đó luôn bị khử**, không cần ai đăng ký
gì cả. Tính chất đó là cấu trúc, không phải kỷ luật.

`THE_RANH_GIOI` vẫn tồn tại để khử THÊM các thẻ khác — chặn cả kiểu tấn công dựng
một khối `<tai_lieu>` giả bên trong một vùng khác. Có test quét mã nguồn, bắt mọi
thẻ đang được dùng phải nằm trong tập này, nên quên đăng ký là test đỏ.
"""

from __future__ import annotations

import re

# Mọi thẻ hệ thống dùng làm ranh giới. Test `test_the_ranh_gioi_day_du` quét
# nguồn và đối chiếu, nên danh sách này không lệch khỏi thực tế được.
THE_RANH_GIOI: frozenset[str] = frozenset(
    {
        # Bài thơ đã xong, đưa cho lượt đặt tiêu đề đọc (QĐ-TD-1). Là DỮ LIỆU để
        # đọc, không phải lệnh — và chính vì bài thơ do mô hình viết ra nên nó
        # càng phải bọc thẻ: một bài chứa dòng trông như chỉ dẫn sẽ bị khử ở đây.
        "bai_tho",
        "bien_ban_kiem_dinh",
        "chi_dan_tu_nguoi_dung",
        "ke_hoach_bat_buoc",
        "phan_da_viet",
        "tai_lieu",
        "thong_tin_nguoi_dung",
        "tom_tat",
        "vi_du_dung_luat",
        "yeu_cau_bai_tho",
        # Bốn tên dưới đây không được dùng làm ranh giới, nhưng giữ lại để khử:
        # chúng hay xuất hiện trong các mẫu tiêm lệnh nhắm vào hệ RAG.
        "context",
        "tool_result",
        "fact",
        "prompt",
    }
)


def _mau_khu(ten_the: set[str]) -> re.Pattern[str]:
    ten = "|".join(sorted(re.escape(t) for t in ten_the))
    # `</?…[^>]*>` bắt cả thẻ mở có thuộc tính lẫn thẻ đóng.
    return re.compile(rf"</?(?:{ten})[^>]*>", re.IGNORECASE)


_MAU_MAC_DINH = _mau_khu(set(THE_RANH_GIOI))


def sanitize_tag_lookalikes(content: str) -> str:
    """Khử mọi thẻ ranh giới đã biết khỏi nội dung."""
    return _MAU_MAC_DINH.sub("", content)


def wrap_xml_tag(tag_name: str, content: str, attributes: str = "") -> str:
    """Bọc nội dung vào thẻ, sau khi khử mọi thẻ có thể phá ranh giới.

    BẤT BIẾN: chuỗi trả về chứa ĐÚNG một thẻ mở `tag_name` và ĐÚNG một thẻ đóng
    `tag_name`. Điều này đúng kể cả khi `tag_name` chưa có trong `THE_RANH_GIOI`
    — đó là điểm khác căn bản so với bản cũ, và là lý do một thẻ mới thêm vào
    không tạo ra lỗ hổng ngay từ lúc nó ra đời.
    """
    sach = _mau_khu(set(THE_RANH_GIOI) | {tag_name}).sub("", content)
    attr_str = f" {attributes}" if attributes else ""
    return f"<{tag_name}{attr_str}>\n{sach}\n</{tag_name}>"
