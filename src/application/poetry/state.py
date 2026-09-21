"""§31 STATE MACHINE — 14 trạng thái của một yêu cầu làm thơ.

VÌ SAO DỰNG THẬT CHỨ KHÔNG CHỈ VẼ. Một máy trạng thái chỉ nằm trong tài liệu thì
không ai biết hệ thống đang ở đâu khi có sự cố. Ở đây nó là DỮ LIỆU: mỗi lần
chuyển trạng thái được ghi lại kèm lý do, và bảng chuyển hợp lệ được cưỡng chế.

⛔ KHÔNG VẼ TRẠNG THÁI CHƯA DÙNG RỒI ĐỂ ĐÓ. Mỗi trạng thái dưới đây đều có ít nhất
một đường đi thật dẫn tới nó, trừ ba trạng thái HITL được đánh dấu rõ là thuộc G7.
Mã chết trông như mã chạy là kiểu nợ tệ nhất.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias

TrangThai: TypeAlias = Literal[
    "RECEIVED",
    "VALIDATED",
    "ANALYZING",
    "NEED_CLARIFICATION",
    "WAIT_USER",
    "RESEARCHING",
    "PLANNING",
    "GENERATING",
    "VERIFYING",
    "REVISING",
    "VERIFIED",
    "SAFETY_CHECK",
    "HITL_DECISION",
    "FINAL_RESPONSE",
    "FEEDBACK",
    "END",
]

# Bảng chuyển hợp lệ. Thiếu bảng này thì "máy trạng thái" chỉ là một cái enum.
CHUYEN_HOP_LE: dict[TrangThai, frozenset[TrangThai]] = {
    "RECEIVED": frozenset({"VALIDATED", "END"}),
    "VALIDATED": frozenset({"ANALYZING", "END"}),
    "ANALYZING": frozenset({"NEED_CLARIFICATION", "RESEARCHING", "PLANNING"}),
    "NEED_CLARIFICATION": frozenset({"WAIT_USER"}),
    "WAIT_USER": frozenset({"ANALYZING", "END"}),
    "RESEARCHING": frozenset({"PLANNING"}),
    "PLANNING": frozenset({"GENERATING", "END"}),
    "GENERATING": frozenset({"VERIFYING", "END"}),
    "VERIFYING": frozenset({"REVISING", "VERIFIED", "END"}),
    "REVISING": frozenset({"VERIFYING", "END"}),
    "VERIFIED": frozenset({"SAFETY_CHECK"}),
    "SAFETY_CHECK": frozenset({"HITL_DECISION", "FINAL_RESPONSE", "END"}),
    "HITL_DECISION": frozenset({"FINAL_RESPONSE", "WAIT_USER", "END"}),
    "FINAL_RESPONSE": frozenset({"FEEDBACK", "END"}),
    "FEEDBACK": frozenset({"END"}),
    "END": frozenset(),
}


@dataclass(frozen=True, slots=True)
class BuocChuyen:
    tu: TrangThai
    den: TrangThai
    ly_do: str


class ChuyenTrangThaiSai(Exception):
    """Chuyển sang một trạng thái không có trong bảng.

    Là NGOẠI LỆ chứ không phải `Result`: đây là lỗi lập trình, không phải tình
    huống nghiệp vụ. Đúng quy ước 1.4 — `Result` ở biên, ngoại lệ cho lỗi code.
    """


@dataclass(slots=True)
class DauVetTrangThai:
    """Vết đi của một yêu cầu. Có trạng thái, dùng cho đúng MỘT yêu cầu."""

    hien_tai: TrangThai = "RECEIVED"
    lich_su: list[BuocChuyen] = field(default_factory=list)

    def chuyen(self, den: TrangThai, ly_do: str = "") -> None:
        if den not in CHUYEN_HOP_LE[self.hien_tai]:
            raise ChuyenTrangThaiSai(
                f"không có đường {self.hien_tai} -> {den}; "
                f"hợp lệ: {sorted(CHUYEN_HOP_LE[self.hien_tai])}"
            )
        self.lich_su.append(BuocChuyen(tu=self.hien_tai, den=den, ly_do=ly_do))
        self.hien_tai = den

    def duong_di(self) -> tuple[TrangThai, ...]:
        return ("RECEIVED", *(b.den for b in self.lich_su))
