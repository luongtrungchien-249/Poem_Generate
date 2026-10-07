"""Poetry jobs only expose pure checks; no recursive generation or external I/O."""

from application.ports.llm import CallContext, ToolCall, ToolResult
from application.ports.tools import ToolPort, ToolSpec

ALLOWED = frozenset({"kiem_tra_tho", "danh_gia_chat_luong_tho"})


class PoetryTools:
    def __init__(self, inner: ToolPort) -> None:
        self.inner = inner

    def specs(self) -> tuple[ToolSpec, ...]:
        return tuple(spec for spec in self.inner.specs() if spec.name in ALLOWED)

    async def call_many(
        self, calls: tuple[ToolCall, ...], ctx: CallContext
    ) -> tuple[ToolResult, ...]:
        allowed = tuple(call for call in calls if call.name in ALLOWED)
        results = {result.call_id: result for result in await self.inner.call_many(allowed, ctx)}
        return tuple(
            results[call.id]
            if call.name in ALLOWED
            else ToolResult(
                call_id=call.id,
                content="Tool không được phép trong tác vụ sinh thơ.",
                is_error=True,
            )
            for call in calls
        )
