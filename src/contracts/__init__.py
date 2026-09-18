"""Common Pydantic data contracts across AI Platform."""

from .chat import ChatRequest, ChatResponse, Message, Role, StreamDelta
from .chunk import Chunk, Document, EnrichedChunk, RetrievalResult
from .error import ErrorCode, ErrorResponse
from .feedback import FeedbackRecord, FeedbackRequest
from .trace import SpanEvent, TraceContext

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "StreamDelta",
    "Message",
    "Role",
    "TraceContext",
    "SpanEvent",
    "Document",
    "Chunk",
    "EnrichedChunk",
    "RetrievalResult",
    "FeedbackRequest",
    "FeedbackRecord",
    "ErrorResponse",
    "ErrorCode",
]
