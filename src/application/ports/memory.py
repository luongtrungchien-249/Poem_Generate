from dataclasses import dataclass
from typing import Protocol

from domain.conversation.message import StoredMessage
from domain.conversation.thread import ThreadScope


@dataclass(frozen=True, slots=True)
class Fact:
    id: str
    subject_id: str
    text: str
    confidence: float
    created_at_epoch: float


class MemoryPort(Protocol):
    """Port for persistent conversation memory and long-term user facts.
    LAW L3: Every method MUST take ThreadScope as its FIRST parameter to strictly prevent cross-thread leaks.
    """

    async def append(self, scope: ThreadScope, msg: StoredMessage) -> None: ...

    async def recent(self, scope: ThreadScope, limit: int) -> tuple[StoredMessage, ...]: ...

    async def facts(self, scope: ThreadScope, subject_id: str, query: str) -> tuple[Fact, ...]: ...

    async def summary(self, scope: ThreadScope) -> str | None: ...

    async def forget(self, scope: ThreadScope, actor_id: str, pattern: str) -> tuple[Fact, ...]: ...

    async def stage_forget(self, scope: ThreadScope, actor_id: str, fact_ids: tuple[str, ...]) -> None: ...

    async def confirm_forget(self, scope: ThreadScope, actor_id: str, choices: tuple[int, ...]) -> int: ...
