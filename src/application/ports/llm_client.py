"""`LLMClient` — provider khai đủ CẢ BA cổng hẹp.

════ ĐÃ TÁCH BA, 21/09/2026 — ADR-0005 ════

Trước đây đây là một `Protocol` gộp `generate` + `stream` + `embed`, và mọi nơi
đều phụ thuộc vào cả ba dù chỉ dùng một. `rag/retriever.py` chỉ cần `embed()`
nhưng vẫn khai phụ thuộc vào một thứ biết cả hội thoại lẫn phát luồng.

Nay ba trách nhiệm nằm ở ba tệp riêng:

    ports/generation.py   GenerationPort   sinh một lượt, có thể kèm tool
    ports/streaming.py    StreamingPort    phát từng mẩu
    ports/embedding.py    EmbeddingPort    văn bản -> vector

`LLMClient` giữ lại làm tên gọi cho "một provider khai đủ cả ba" — đúng thứ mà
composition root cần khi dựng một client thật.

⛔ QUY TẮC DÙNG, có test kiến trúc cưỡng chế:

    bootstrap/  và  adapters/   ĐƯỢC dùng `LLMClient`
    application/ và entrypoints/ phải dùng CỔNG HẸP mà mình thật sự cần

Vì sao cưỡng chế: phụ thuộc vào cổng gộp là cách âm thầm làm mất tác dụng của việc
tách. Một `HybridRetriever` nhận `LLMClient` thì không thể thay bằng bộ nhúng cục
bộ, dù nó chỉ gọi đúng `embed()`.
"""

from typing import Protocol

from .embedding import EmbeddingPort
from .generation import GenerationPort, LLMResponse, ToolCallOut, ToolSchema
from .streaming import LLMStreamChunk, StreamingPort


class LLMClient(GenerationPort, StreamingPort, EmbeddingPort, Protocol):
    """Provider khai đủ ba cổng. Chỉ composition root và adapter được phụ thuộc vào nó."""


__all__ = [
    "LLMClient",
    "GenerationPort",
    "StreamingPort",
    "EmbeddingPort",
    "LLMResponse",
    "LLMStreamChunk",
    "ToolCallOut",
    "ToolSchema",
]
