from dataclasses import dataclass
from typing import Protocol, TypeAlias

from domain.conversation.thread import ThreadScope


@dataclass(frozen=True, slots=True)
class Pass:
    pass


@dataclass(frozen=True, slots=True)
class Warn:
    tier: str
    retry_after_ms: int


@dataclass(frozen=True, slots=True)
class Silent:
    tier: str
    retry_after_ms: int


RateLimitOutcome: TypeAlias = Pass | Warn | Silent


class RateLimitPort(Protocol):
    """Port checking per-user / per-thread rate limits and daily token budgets."""

    async def check(self, scope: ThreadScope, sender_id: str) -> RateLimitOutcome: ...

    async def should_warn(self, scope: ThreadScope, sender_id: str) -> bool: ...

    async def within_daily_budget(self, scope: ThreadScope) -> bool: ...
