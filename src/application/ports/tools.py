from dataclasses import dataclass
from typing import Any, Protocol

from .llm import CallContext, ToolCall, ToolResult


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """Slim tool representation sent upstream to LLM."""
    name: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """Rich tool representation for developers (requirements, failure modes, timeouts)."""
    spec: ToolSpec
    timeout_sec: float = 5.0
    failure_modes: tuple[str, ...] = ()
    is_mutation: bool = False


class ToolPort(Protocol):
    """Port executing external tools and APIs."""

    def specs(self) -> tuple[ToolSpec, ...]: ...

    async def call_many(
        self,
        calls: tuple[ToolCall, ...],
        ctx: CallContext,
    ) -> tuple[ToolResult, ...]: ...
