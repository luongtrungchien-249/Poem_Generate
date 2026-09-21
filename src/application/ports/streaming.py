"""Cổng PHÁT LUỒNG — trả lời từng mẩu.

Tách khỏi `LLMClient` ngày 21/09/2026 theo ADR-0005.

VÌ SAO LÀ MỘT CỔNG RIÊNG. `stream()` và `reply()` trả về hai thứ khác loại:

    reply()   MỘT lượt trọn vẹn, có `tool_calls`, bọc trong `Result`
    stream()  MỘT DÒNG các mẩu, không có tool, không bọc `Result`

Khác nhau tới mức không gộp được: một mẩu đang phát dở thì chưa có gì để phán là
thành công hay thất bại, nên `Result` không có chỗ đặt.

⚠️ AI DÙNG CỔNG NÀY PHẢI ĐỌC: mẩu phát ra KHÔNG đi thẳng tới người dùng. Nó phải
qua `domain.guardrails.output.streaming.StreamingOutputGuard` trước — byte đã gửi
thì không thu về được.
"""

from collections.abc import AsyncIterator
from typing import Any, Protocol

from pydantic import BaseModel

from contracts.chat import Message


class LLMStreamChunk(BaseModel):
    delta: str
    finish_reason: str | None = None
    usage: dict[str, Any] | None = None


class StreamingPort(Protocol):
    """Phát câu trả lời theo từng mẩu."""

    # KHÔNG phải `async def`: mọi hiện thực đều là async generator, nên gọi hàm
    # này trả thẳng AsyncIterator chứ không trả coroutine. Khai `async def` ở đây
    # nghĩa là "coroutine trả về AsyncIterator", buộc nơi gọi phải `await` trước
    # khi lặp — trái với cách adapter thật hoạt động.
    def stream(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[LLMStreamChunk]: ...
