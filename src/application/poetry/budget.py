"""Admission of model calls shared by all calls in a single job."""

from typing import Any

from application.ports.llm import CallContext, CheapRoute, LlmMessage, LlmPort, LlmReply
from application.ports.rate_limit import RateLimitPort
from domain.common.errors import BotError, BudgetExceeded
from domain.common.result import Err, Result
from domain.conversation.thread import ThreadScope


class JobBudgetLlm:
    def __init__(
        self, inner: LlmPort, limiter: RateLimitPort, tenant_id: str, max_calls: int
    ) -> None:
        self.inner = inner
        self.limiter = limiter
        self.scope = ThreadScope(platform="web", thread_id=f"ngansach:{tenant_id}")
        self.max_calls = max_calls
        self.calls = 0

    async def _reserve(self) -> bool:
        # Increment before await so concurrent candidate requests cannot race.
        if self.calls >= self.max_calls:
            return False
        self.calls += 1
        return await self.limiter.within_daily_budget(self.scope)

    async def reply(
        self,
        messages: tuple[LlmMessage, ...],
        tools: tuple[Any, ...],
        ctx: CallContext,
        model: str | None = None,
    ) -> Result[LlmReply, BotError]:
        if not await self._reserve():
            return Err(
                BudgetExceeded(
                    scope_name=self.scope.thread_id, limit=self.max_calls, current=self.calls
                )
            )
        return await self.inner.reply(messages=messages, tools=tools, ctx=ctx, model=model)

    async def cheap(
        self, messages: tuple[LlmMessage, ...], route: CheapRoute, ctx: CallContext
    ) -> Result[str, BotError]:
        if not await self._reserve():
            return Err(
                BudgetExceeded(
                    scope_name=self.scope.thread_id, limit=self.max_calls, current=self.calls
                )
            )
        return await self.inner.cheap(messages=messages, route=route, ctx=ctx)
