from typing import Any

from application.ports.llm import (
    CallContext,
    CheapRoute,
    LlmMessage,
    LlmReply,
    LlmUsage,
    ToolCall,
)
from application.ports.memory import Fact
from application.ports.rate_limit import Pass, RateLimitOutcome
from application.ports.tools import ToolResult, ToolSpec
from domain.common.errors import BotError
from domain.common.result import Ok, Result
from domain.conversation.message import OutboundMessage, StoredMessage
from domain.conversation.thread import ThreadScope


class FakeLlmPort:
    def __init__(self, canned_response: str = "Câu trả lời giả lập từ FakeLlmPort") -> None:
        self.canned_response = canned_response
        self.recorded_calls: list[tuple[LlmMessage, ...]] = []

    async def reply(
        self,
        messages: tuple[LlmMessage, ...],
        tools: tuple[Any, ...],
        ctx: CallContext,
        model: str | None = None,
    ) -> Result[LlmReply, BotError]:
        self.recorded_calls.append(messages)
        return Ok(
            LlmReply(
                text=self.canned_response,
                tool_calls=(),
                usage=LlmUsage(input_tokens=10, output_tokens=10),
            )
        )

    async def cheap(
        self,
        messages: tuple[LlmMessage, ...],
        route: CheapRoute,
        ctx: CallContext,
    ) -> Result[str, BotError]:
        return Ok("fake_classification")


class FakeMemoryPort:
    def __init__(self) -> None:
        self.history: list[StoredMessage] = []
        self.facts_store: list[Fact] = []

    async def append(self, scope: ThreadScope, msg: StoredMessage) -> None:
        self.history.append(msg)

    async def recent(self, scope: ThreadScope, limit: int) -> tuple[StoredMessage, ...]:
        return tuple(self.history[-limit:])

    async def facts(self, scope: ThreadScope, subject_id: str, query: str) -> tuple[Fact, ...]:
        return tuple(self.facts_store)

    async def summary(self, scope: ThreadScope) -> str | None:
        return "Tóm tắt giả lập"

    async def forget(self, scope: ThreadScope, actor_id: str, pattern: str) -> tuple[Fact, ...]:
        return ()

    async def stage_forget(self, scope: ThreadScope, actor_id: str, fact_ids: tuple[str, ...]) -> None:
        pass

    async def confirm_forget(self, scope: ThreadScope, actor_id: str, choices: tuple[int, ...]) -> int:
        return 0


class FakeToolPort:
    def specs(self) -> tuple[ToolSpec, ...]:
        return (
            ToolSpec(
                name="search_kb",
                description="Fake search KB",
                parameters={"type": "object", "properties": {"q": {"type": "string"}}},
            ),
        )

    async def call_many(self, calls: tuple[ToolCall, ...], ctx: CallContext) -> tuple[ToolResult, ...]:
        return tuple(ToolResult(call_id=c.id, content="Fake tool output") for c in calls)


class FakeRateLimitPort:
    async def check(self, scope: ThreadScope, sender_id: str) -> RateLimitOutcome:
        return Pass()

    async def should_warn(self, scope: ThreadScope, sender_id: str) -> bool:
        return False

    async def within_daily_budget(self, scope: ThreadScope) -> bool:
        return True


class FakeChannelPort:
    def __init__(self) -> None:
        self.sent_messages: list[tuple[ThreadScope, OutboundMessage]] = []
        self.typing_called: list[ThreadScope] = []

    @property
    def max_message_chars(self) -> int:
        return 2000

    async def typing(self, scope: ThreadScope) -> None:
        self.typing_called.append(scope)

    async def send(self, scope: ThreadScope, msg: OutboundMessage) -> None:
        self.sent_messages.append((scope, msg))


class FakeLoggerPort:
    def debug(self, msg: str, **kwargs: Any) -> None: pass
    def info(self, msg: str, **kwargs: Any) -> None: pass
    def warning(self, msg: str, **kwargs: Any) -> None: pass
    def error(self, msg: str, **kwargs: Any) -> None: pass
    def bind(self, **kwargs: Any) -> "FakeLoggerPort": return self
