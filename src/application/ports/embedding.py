"""Cổng NHÚNG — văn bản thành vector.

Tách khỏi `LLMClient` ngày 21/09/2026 theo ADR-0005.

VÌ SAO LÀ MỘT CỔNG RIÊNG. Nhúng không phải hội thoại: không có lượt, không có
tool, không có trạng thái. Một bộ nhúng cục bộ (sentence-transformers chạy trên
máy) là hiện thực hoàn toàn hợp lệ của cổng này, và nó KHÔNG có `reply()` cũng
không có `stream()` để mà khai.

Bắt nó khai hai phương thức đó chỉ để lọt qua một `Protocol` gộp là buộc mọi hiện
thực mang theo `NotImplementedError` — dấu hiệu kinh điển của giao diện bị gộp sai.
"""

from typing import Protocol


class EmbeddingPort(Protocol):
    """Biến văn bản thành vector."""

    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> list[list[float]]:
        """Trả về đúng `len(texts)` vector, cùng thứ tự với đầu vào.

        Hợp đồng về THỨ TỰ là bắt buộc: nơi gọi ghép vector với văn bản theo chỉ
        số, nên một hiện thực trả về khác thứ tự sẽ gán sai vector cho mọi văn bản
        mà không có gì báo lỗi.
        """
        ...
