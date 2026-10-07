"""Durable job boundary. Payload and progress contain no intermediate poems."""

from dataclasses import dataclass, field
from typing import Any, Protocol

from domain.conversation.tenant import TenantScope

TERMINAL = frozenset({"completed", "failed", "cancelled", "expired"})


@dataclass(frozen=True)
class PoemJob:
    job_id: str
    tenant_id: str
    status: str
    created_at: float
    updated_at: float
    deadline: float
    payload: dict[str, Any] = field(repr=False)
    model: str = ""
    provider: str = ""
    owner: str = ""
    progress: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] | None = None
    result_status: int | None = None
    error: str | None = None


class JobConflict(ValueError):
    pass


class JobLimit(ValueError):
    pass


class PoemJobStore(Protocol):
    async def create(
        self,
        scope: TenantScope,
        payload: dict[str, Any],
        key: str,
        *,
        model: str,
        provider: str,
        deadline_seconds: float,
        active_limit: int,
    ) -> PoemJob: ...

    async def get(self, scope: TenantScope, job_id: str) -> PoemJob | None: ...

    async def cancel(self, scope: TenantScope, job_id: str) -> PoemJob | None: ...

    async def list_active(self, scope: TenantScope, conversation_id: str) -> list[PoemJob]: ...

    async def claim(self, owner: str, lease_seconds: float) -> PoemJob | None: ...

    async def touch(
        self,
        scope: TenantScope,
        job_id: str,
        owner: str,
        status: str,
        progress: dict[str, Any],
        lease_seconds: float,
    ) -> bool: ...

    async def finish(
        self,
        scope: TenantScope,
        job_id: str,
        owner: str,
        *,
        status: str,
        result: dict[str, Any] | None = None,
        result_status: int | None = None,
        error: str | None = None,
    ) -> bool: ...

    async def cleanup(self, ttl_seconds: float) -> None: ...
