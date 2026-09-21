"""§22 HITL DECISION ENGINE — khi nào máy tự trả lời, khi nào đưa cho người.

THUẦN và TẤT ĐỊNH: sáu số vào, một quyết định ra. Không I/O, không LLM. Đặt ở
`domain/` vì đây là luật nghiệp vụ, không phải hạ tầng.

════ MỘT ĐỊNH NGHĨA ĐÃ PHẢI VIẾT LẠI ════

§22.3 định nghĩa Human-as-tiebreaker là lúc *"Rule Checker A ≠ Rule Checker B"*.

Với kiến trúc này, tình huống đó **không bao giờ xảy ra**: chỉ có MỘT bộ kiểm luật
(`rule.py`), và nó tất định. Giữ nguyên định nghĩa ấy là dựng một nhánh code chết.

QĐ-D3 đã định nghĩa lại, và đây là bản thi hành: tiebreaker là lúc **hai loại bằng
chứng KHÁC LOẠI nói ngược nhau** —

    luật nói ĐẠT   (rule.py, tất định, thẩm quyền cao)
    chất lượng nói CHƯA  (chuẩn dự án, có ngưỡng tuỳ ý)

Máy không có cơ sở nào để chọn bên, vì hai bên trả lời hai câu hỏi khác nhau. Đó
mới là mâu thuẫn có thật, và mới là chỗ cần người phân xử.

════ VÌ SAO KHÔNG CHẤM ĐIỂM TỔNG RỒI SO NGƯỠNG ════

Cách làm quen thuộc là cộng các tín hiệu thành một điểm rồi cắt theo ngưỡng. Ở đây
cố ý KHÔNG làm vậy: một điểm tổng trộn lẫn "bài sai luật" với "chủ đề nhạy cảm",
và khi cần giải thích cho reviewer thì không tách ra được nữa.

Thay vào đó là một chuỗi luật có THỨ TỰ, mỗi luật nêu đúng một lý do.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias

QuyetDinhHitl: TypeAlias = Literal[
    "AUTO_RESPOND", "ASK_USER", "HUMAN_REVIEW", "HUMAN_TIEBREAKER", "REJECT"
]


@dataclass(frozen=True, slots=True)
class TinHieuHitl:
    """Sáu đầu vào của §22, đúng tên tài liệu đặt."""

    yeu_cau_day_du: bool
    an_toan_dat: bool
    dat_luat: bool
    dat_chat_luong: bool
    so_luot_sua: int
    chu_de_can_xem_lai: bool = False
    # Trần lượt sửa của lần chạy này. Chạm trần nghĩa là vòng sửa đã kiệt sức.
    tran_luot_sua: int = 3


@dataclass(frozen=True, slots=True)
class KetQuaHitl:
    quyet_dinh: QuyetDinhHitl
    ly_do: str


def quyet_dinh_hitl(t: TinHieuHitl) -> KetQuaHitl:
    """Chuỗi luật có thứ tự. Luật đầu tiên khớp là luật thắng.

    THỨ TỰ LÀ MỘT PHẦN CỦA LUẬT, không phải chi tiết cài đặt:
    an toàn trước, rồi tính đầy đủ, rồi luật thơ, rồi chất lượng.
    """
    # 1. An toàn đứng đầu. Không có gì đổi được kết luận này.
    if not t.an_toan_dat:
        return KetQuaHitl("REJECT", "đầu ra không qua rào an toàn")

    # 2. Thiếu thông tin thì hỏi người DÙNG, không đẩy cho người DUYỆT.
    #    Reviewer không biết người dùng muốn gì hơn chính người dùng.
    if not t.yeu_cau_day_du:
        return KetQuaHitl("ASK_USER", "yêu cầu chưa đủ thông tin")

    # 3. Sai luật mà đã hết lượt sửa -> từ chối. Không đưa người duyệt một bài sai
    #    luật: bộ kiểm đã tất định, người xem lại không đổi được phán quyết ấy.
    if not t.dat_luat:
        if t.so_luot_sua >= t.tran_luot_sua:
            return KetQuaHitl("REJECT", "hết lượt sửa mà bài vẫn sai luật")
        return KetQuaHitl("REJECT", "bài sai luật")

    # 4. TIEBREAKER — hai loại bằng chứng khác loại nói ngược nhau (QĐ-D3).
    if t.dat_luat and not t.dat_chat_luong:
        return KetQuaHitl(
            "HUMAN_TIEBREAKER",
            "luật nói ĐẠT nhưng chất lượng nói CHƯA — máy không có cơ sở chọn bên",
        )

    # 5. Chủ đề ở mức REVIEW: bài ổn về mọi mặt đo được, nhưng nội dung nên có
    #    người nhìn qua. Đây là dòng "Bias -> Human review" của bảng §20.
    if t.chu_de_can_xem_lai:
        return KetQuaHitl("HUMAN_REVIEW", "chủ đề được đánh dấu cần xem lại")

    # 6. Sửa nhiều lượt mới đạt: bài hợp lệ, nhưng số lượt cao là tín hiệu bài khó
    #    hoặc prompt có vấn đề — đáng để người nhìn, không đáng để chặn.
    if t.so_luot_sua >= t.tran_luot_sua:
        return KetQuaHitl(
            "HUMAN_REVIEW", f"phải sửa {t.so_luot_sua} lượt mới đạt — chạm trần"
        )

    return KetQuaHitl("AUTO_RESPOND", "đủ thông tin, an toàn, đúng luật, đạt chất lượng")


def duoc_tra_thang(q: QuyetDinhHitl) -> bool:
    """Chỉ `AUTO_RESPOND` được trả thẳng ra người dùng mà không qua ai.

    Viết thành một hàm riêng thay vì so chuỗi rải rác: thêm một quyết định mới mà
    quên cập nhật nơi nào đó là cách để một bài chưa duyệt lọt ra.
    """
    return q == "AUTO_RESPOND"
