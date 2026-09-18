"""Port kiểm định đầu ra có ràng buộc.

Cổng này TỔNG QUÁT, không gắn cứng vào thơ. Thơ chỉ là hiện thực đầu tiên; sau này
ràng buộc JSON schema, bắt buộc trích dẫn hay giới hạn độ dài đều cắm vào đúng khe
này mà không phải sửa vòng sinh.

Hai tính chất bắt buộc của một hiện thực:
  1. ĐỒNG BỘ và THUẦN — không I/O. Cổng chặn không được phép trượt vì mạng.
  2. TẤT ĐỊNH — cùng đầu vào cho cùng phán quyết. Nếu không, vòng sửa sẽ dao động.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class OutputSpec:
    """Mô tả ràng buộc mà đầu ra phải thoả.

    `ma_the` chọn bộ kiểm; `tham_so` là tuỳ chọn của riêng bộ kiểm đó (số dòng
    mong muốn, sơ đồ vần mong muốn…). Không bộ kiểm nào được coi tham số lạ là lỗi.
    """

    ma_the: str
    tham_so: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class LoiKiemDinh:
    """Một vi phạm, đã quy về dạng chung để vòng sửa dùng được mà không cần biết thể loại."""

    ma: str
    dia_chi: str  # "D3" hoặc "toàn bài" — đủ để mô tả cho người và cho mô hình
    ky_vong: str
    thuc_te: str
    goi_y: str


@dataclass(frozen=True, slots=True)
class KetQuaKiemDinh:
    """Phán quyết chung. Chỉ `dat` có quyền chặn đầu ra."""

    dat: bool
    loi: tuple[LoiKiemDinh, ...]
    bien_ban: str  # văn bản gửi lại mô hình khi chưa đạt; rỗng khi đã đạt
    mo_ta_mem: tuple[str, ...] = ()  # số liệu tham khảo, không bao giờ chặn


class OutputVerifier(Protocol):
    """Bộ kiểm một thể loại đầu ra."""

    ma_the: str

    def kiem(self, van_ban: str, spec: OutputSpec) -> KetQuaKiemDinh: ...
