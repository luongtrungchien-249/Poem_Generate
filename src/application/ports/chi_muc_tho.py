"""Cổng CHỈ MỤC DÒNG THƠ CÓ SẴN — phát hiện chép (Plan_PoeTone GĐ1.3, QĐ-P2).

Đọc kho là I/O, nên `application/` chỉ khai cổng; hiện thực ở `adapters/`.

Khoá tra là dòng đã chuẩn hoá bằng `application.poetry.doi_chieu_chep.khoa_dong` —
adapter PHẢI dựng chỉ mục bằng đúng hàm đó, nếu không hai bên so hai thứ khác nhau
và phép kiểm im lặng không bắt được gì.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class NguonDong:
    """Nơi một dòng thơ đã xuất hiện. Đủ để ghi nguồn (kho HF là CC-BY-4.0)."""

    kho: str
    tieu_de: str = ""
    tac_gia: str = ""
    url: str = ""


class ChiMucDongThoPort(Protocol):
    def tim(self, khoa: str) -> NguonDong | None:
        """Nguồn của dòng có khoá `khoa`, hoặc None nếu chưa thấy ở đâu.

        ĐỒNG BỘ và không lỗi mạng: cổng chặn gọi hàm này, và cổng chặn không được
        phép trượt vì I/O (hợp đồng `OutputVerifier`). Hiện thực nạp một lần rồi
        tra trong bộ nhớ.
        """
        ...
