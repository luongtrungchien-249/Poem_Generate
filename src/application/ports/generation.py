"""Cổng SINH MỘT PHÁT — một lượt vào, một lượt ra, có thể kèm lời gọi tool.

Tách khỏi `LLMClient` ngày 21/09/2026 theo ADR-0005.

Khác `LlmPort` ở `ports/llm.py`: cổng này dùng DTO Pydantic của `contracts.chat`
và ném ngoại lệ, còn `LlmPort` dùng tagged union thuần và trả `Result`. `LlmPort`
là đường đi chính thức của nghiệp vụ; cổng này là hình dạng thô mà các provider
nói. `adapters/llm/chat_port.py` dịch giữa hai bên.
"""

from typing import Any, Protocol

from pydantic import BaseModel, Field

from contracts.chat import Message


class ToolCallOut(BaseModel):
    """Một lời gọi tool do mô hình sinh ra.

    `arguments` giữ nguyên dạng CHUỖI JSON chứ không parse sẵn. Lý do: mô hình
    thỉnh thoảng sinh JSON hỏng, và chỗ đúng để phát hiện điều đó là nơi thực thi
    tool — nơi có thể trả lỗi lại cho mô hình sửa. Parse ở đây thì lỗi thành ngoại
    lệ giữa tầng adapter, và mô hình không bao giờ biết nó đã viết sai.
    """

    id: str
    name: str
    arguments: str


class LLMResponse(BaseModel):
    content: str
    model: str
    finish_reason: str = "stop"
    usage: dict[str, Any] = Field(default_factory=dict)
    cost_usd: float = 0.0
    raw_response: dict[str, Any] | None = None
    # Rỗng nghĩa là mô hình trả lời thẳng, không xin gọi tool nào.
    tool_calls: list[ToolCallOut] = Field(default_factory=list)


# Lược đồ tool TRUNG LẬP giữa các nhà cung cấp: {"name", "description", "parameters"}.
# Mỗi adapter tự dịch sang định dạng riêng — OpenAI bọc trong {"type":"function"},
# Anthropic đổi khoá "parameters" thành "input_schema". Giữ dạng trung lập ở port
# để đổi provider không phải sửa nơi định nghĩa tool.
ToolSchema = dict[str, Any]


class GenerationPort(Protocol):
    """Sinh một lượt trả lời, có thể kèm lời gọi tool."""

    async def generate(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[ToolSchema] | None = None,
        **kwargs: Any,
    ) -> LLMResponse: ...
