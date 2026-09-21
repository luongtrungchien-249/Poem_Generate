"""Cổng kho khoá API — G13.

Tách port vì việc tra khoá xảy ra ở MỌI request: hiện thực có thể là DB, có thể là
bảng trong bộ nhớ cho dev, sau này có thể là một dịch vụ danh tính riêng. Tầng
middleware không được biết điều đó.
"""

from typing import Protocol

from domain.policy.api_key import BanGhiKhoa


class ApiKeyStorePort(Protocol):
    """Kho khoá đã phát hành."""

    async def tra(self, bam: str) -> BanGhiKhoa | None:
        """Tra bản ghi theo BĂM của khoá. Không có thì None.

        Nhận băm chứ không nhận khoá nguyên văn: hiện thực không cần biết khoá thật,
        nên nó cũng không thể vô tình ghi khoá thật vào log.
        """
        ...

    async def phat_hanh(
        self, tenant_id: str, *, ten: str = "", song_giay: float | None = None
    ) -> str:
        """Phát hành khoá mới, trả về khoá NGUYÊN VĂN.

        Đây là lần DUY NHẤT khoá nguyên văn tồn tại ngoài tay người dùng — kho chỉ
        lưu băm. Mất thì phát hành khoá mới, không có đường lấy lại.
        """
        ...

    async def thu_hoi(self, bam: str) -> bool:
        """Thu hồi. Có hiệu lực NGAY, không cần khởi động lại."""
        ...
