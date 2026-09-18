from dataclasses import dataclass
from typing import Any, Literal, Protocol, TypeAlias

from domain.common.errors import BotError
from domain.common.result import Result
from domain.conversation.thread import ThreadScope


@dataclass(frozen=True, slots=True)
class CallContext:
    scope: ThreadScope
    sender_id: str
    trace_id: str


@dataclass(frozen=True, slots=True)
class ToolCall:
    id: str # Mandatory, never optional
    name: str
    arguments: str


@dataclass(frozen=True, slots=True)
class ToolResult:
    call_id: str
    content: str
    is_error: bool = False


@dataclass(frozen=True, slots=True)
class UserMessage:
    content: str


@dataclass(frozen=True, slots=True)
class AssistantMessage:
    content: str = ""
    tool_calls: tuple[ToolCall, ...] = ()


@dataclass(frozen=True, slots=True)
class ToolMessage:
    tool_call_id: str
    content: str


LlmMessage: TypeAlias = UserMessage | AssistantMessage | ToolMessage


@dataclass(frozen=True, slots=True)
class LlmUsage:
    input_tokens: int # Fully priced input tokens after subtracting cache
    output_tokens: int
    cached_tokens: int = 0


@dataclass(frozen=True, slots=True)
class LlmReply:
    text: str
    tool_calls: tuple[ToolCall, ...]
    usage: LlmUsage


CheapRoute = Literal["classify", "extract", "short_summary", "rag_eval"]


class LlmPort(Protocol):
    """Port for communicating with LLM providers."""

    async def reply(
        self,
        messages: tuple[LlmMessage, ...],
        tools: tuple[Any, ...],
        ctx: CallContext,
        model: str | None = None,
    ) -> Result[LlmReply, BotError]: ...

    async def cheap(
        self,
        messages: tuple[LlmMessage, ...],
        route: CheapRoute,
        ctx: CallContext,
    ) -> Result[str, BotError]: ...
