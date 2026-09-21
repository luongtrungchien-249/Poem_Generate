"""§19.4 — cấm tuyên bố "đã đúng luật" khi không có bằng chứng kiểm định.

Đây là rail DUY NHẤT của hệ thống chặn *lời nói về kết quả*, chứ không chặn *kết quả*.

Vì sao cần: §18 điều 4 của tài liệu đích dặn mô hình *"Never claim verification
without tool evidence"*. Nhưng dặn trong prompt không phải là bảo đảm — đó là câu
mở đầu của `verify_output.py`: *"prompt không phải là bảo đảm"*. Một mô hình viết
"Bài trên hoàn toàn đúng luật thất ngôn tự do" kèm một bài 6 tiếng thì người dùng
tin nó, không tin bảng bằng chứng.

Thuần, không I/O, không phụ thuộc gì ngoài `re` — đúng chỗ của vòng domain.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Các cách nói "bài này đã được kiểm và đạt". Danh sách nhận diện theo CỤM ĐỘNG TỪ
# + TÍNH TỪ KHẲNG ĐỊNH, không theo từ đơn: "đúng" một mình xuất hiện trong thơ bình
# thường ("đúng hẹn", "đúng mùa") và bắt nó sẽ loại oan.
_MAU_TUYEN_BO = (
    re.compile(r"\b(đã|đều|hoàn toàn|tuyệt đối)?\s*đúng\s+(luật|niêm luật|thể|quy tắc)", re.IGNORECASE),
    re.compile(r"\bđúng\s+chuẩn\b", re.IGNORECASE),
    re.compile(r"\bchuẩn\s+(thất ngôn|thể|luật)\b", re.IGNORECASE),
    re.compile(r"\b(đã|tôi đã)\s+kiểm\s*tra\b.{0,40}\b(đạt|đúng|hợp lệ)", re.IGNORECASE | re.DOTALL),
    re.compile(r"\b(thoả|thỏa)\s*mãn\s+(toàn bộ|mọi|tất cả)?\s*(luật|quy tắc|ràng buộc)", re.IGNORECASE),
    re.compile(r"\b(bảo đảm|đảm bảo)\b.{0,30}\b(đúng luật|hợp luật|đủ 7 tiếng)", re.IGNORECASE),
    re.compile(r"\bkhông\s+(vi phạm|sai)\s+(luật|quy tắc|điều nào)", re.IGNORECASE),
)


@dataclass(frozen=True, slots=True)
class VerificationClaimResult:
    """`allowed=False` nghĩa là văn bản khẳng định một điều nó không chứng minh được."""

    allowed: bool
    claims_found: tuple[str, ...]
    reason: str


def check_verification_claim(
    text: str, *, has_evidence: bool, verdict_passed: bool
) -> VerificationClaimResult:
    """Chặn khi văn bản tuyên bố đúng luật mà bằng chứng không chống lưng.

    Ba đầu vào, cố ý tách rời:
        `text`            lời của mô hình
        `has_evidence`    đã thực sự chạy bộ kiểm chưa
        `verdict_passed`  bộ kiểm có nói đạt không

    Hai cách sai khác nhau đều bị bắt: tuyên bố khi CHƯA kiểm, và tuyên bố khi đã
    kiểm nhưng TRƯỢT. Trường hợp hai nguy hiểm hơn, vì hệ thống có bằng chứng ngược
    lại ngay trong tay mà vẫn để lời khẳng định đi ra.
    """
    tim_thay = tuple(
        m.group(0).strip() for p in _MAU_TUYEN_BO for m in p.finditer(text)
    )
    if not tim_thay:
        return VerificationClaimResult(
            allowed=True, claims_found=(), reason="không có tuyên bố nào về tính đúng luật"
        )

    if not has_evidence:
        return VerificationClaimResult(
            allowed=False,
            claims_found=tim_thay,
            reason=(
                "Văn bản tuyên bố bài đúng luật nhưng CHƯA chạy bộ kiểm — "
                "§19.4 không cho phép khẳng định khi không có bằng chứng."
            ),
        )

    if not verdict_passed:
        return VerificationClaimResult(
            allowed=False,
            claims_found=tim_thay,
            reason=(
                "Văn bản tuyên bố bài đúng luật trong khi bộ kiểm phán TRƯỢT. "
                "Đây là khẳng định trái với bằng chứng đang có."
            ),
        )

    return VerificationClaimResult(
        allowed=True,
        claims_found=tim_thay,
        reason="tuyên bố có bằng chứng kiểm định chống lưng",
    )
