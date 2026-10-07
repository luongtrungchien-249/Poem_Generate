"""SQL queue with atomic leases, fenced writes and tenant-scoped admission."""

import json
import time
import uuid
from typing import Any

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from application.conversation.luu_luot import tieu_de_tu_cau
from application.ports.poem_jobs import TERMINAL, JobConflict, JobLimit, PoemJob
from contracts.chat import Message, Role
from domain.conversation.tenant import TenantScope

from .bang import hoi_thoai, tin_nhan
from .bang import poem_job_gate as gates
from .bang import poem_jobs as jobs


def _load(row: Any) -> PoemJob:
    return PoemJob(
        job_id=row.job_id,
        tenant_id=row.tenant_id,
        status=row.status,
        created_at=row.created_at,
        updated_at=row.updated_at,
        deadline=row.deadline,
        payload=json.loads(row.payload),
        model=row.model,
        provider=row.provider,
        owner=row.owner,
        progress=json.loads(row.progress),
        result=json.loads(row.result) if row.result else None,
        result_status=row.result_status,
        error=row.error,
    )


class SqlPoemJobStore:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    async def create(
        self,
        scope: TenantScope,
        payload: dict[str, Any],
        key: str,
        *,
        model: str,
        provider: str,
        deadline_seconds: float = 300,
        active_limit: int = 2,
    ) -> PoemJob:
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        now = time.time()
        async with self.engine.begin() as conn:
            try:
                async with conn.begin_nested():
                    await conn.execute(insert(gates).values(tenant_id=scope.tenant_id, version=0))
            except IntegrityError:
                pass
            # UPDATE locks in both dialects, including SQLite's writer lock.
            await conn.execute(
                update(gates)
                .where(gates.c.tenant_id == scope.tenant_id)
                .values(version=gates.c.version + 1)
            )
            existing = (
                await conn.execute(
                    select(jobs).where(
                        jobs.c.tenant_id == scope.tenant_id,
                        jobs.c.idempotency_key == key,
                    )
                )
            ).first()
            if existing:
                if existing.payload != raw:
                    raise JobConflict("Idempotency-Key đã được dùng cho yêu cầu khác.")
                return _load(existing)
            await conn.execute(
                update(jobs)
                .where(
                    jobs.c.tenant_id == scope.tenant_id,
                    jobs.c.status.not_in(TERMINAL),
                    jobs.c.deadline <= now,
                )
                .values(status="expired", updated_at=now, owner="", result=None)
            )
            active = await conn.scalar(
                select(func.count())
                .select_from(jobs)
                .where(
                    jobs.c.tenant_id == scope.tenant_id,
                    jobs.c.status.not_in(TERMINAL),
                )
            )
            if int(active or 0) >= active_limit:
                raise JobLimit("Đã đạt giới hạn job đang chạy của tenant.")
            job_id = uuid.uuid4().hex
            await conn.execute(
                insert(jobs).values(
                    tenant_id=scope.tenant_id,
                    job_id=job_id,
                    idempotency_key=key,
                    payload=raw,
                    model=model,
                    provider=provider,
                    status="queued",
                    created_at=now,
                    updated_at=now,
                    deadline=now + deadline_seconds,
                    lease_until=0,
                    owner="",
                    progress="{}",
                )
            )
            row = (
                await conn.execute(
                    select(jobs).where(
                        jobs.c.tenant_id == scope.tenant_id,
                        jobs.c.job_id == job_id,
                    )
                )
            ).one()
            return _load(row)

    async def get(self, scope: TenantScope, job_id: str) -> PoemJob | None:
        async with self.engine.begin() as conn:
            await conn.execute(
                update(jobs)
                .where(
                    jobs.c.tenant_id == scope.tenant_id,
                    jobs.c.job_id == job_id,
                    jobs.c.status.not_in(TERMINAL),
                    jobs.c.deadline <= time.time(),
                )
                .values(status="expired", updated_at=time.time(), owner="", result=None)
            )
            row = (
                await conn.execute(
                    select(jobs).where(
                        jobs.c.tenant_id == scope.tenant_id,
                        jobs.c.job_id == job_id,
                    )
                )
            ).first()
            return _load(row) if row else None

    async def cancel(self, scope: TenantScope, job_id: str) -> PoemJob | None:
        async with self.engine.begin() as conn:
            await conn.execute(
                update(jobs)
                .where(
                    jobs.c.tenant_id == scope.tenant_id,
                    jobs.c.job_id == job_id,
                    jobs.c.status.not_in(TERMINAL),
                )
                .values(status="cancelled", updated_at=time.time(), owner="", result=None)
            )
        return await self.get(scope, job_id)

    async def list_active(self, scope: TenantScope, conversation_id: str) -> list[PoemJob]:
        async with self.engine.connect() as conn:
            rows = (
                await conn.execute(
                    select(jobs)
                    .where(
                        jobs.c.tenant_id == scope.tenant_id,
                        jobs.c.status.not_in(TERMINAL),
                        jobs.c.deadline > time.time(),
                    )
                    .order_by(jobs.c.created_at)
                )
            ).all()
        return [
            job for row in rows if (job := _load(row)).payload.get("session_id") == conversation_id
        ]

    async def claim(self, owner: str, lease_seconds: float = 30) -> PoemJob | None:
        now = time.time()
        async with self.engine.begin() as conn:
            await conn.execute(
                update(jobs)
                .where(
                    jobs.c.status.not_in(TERMINAL),
                    jobs.c.deadline <= now,
                )
                .values(status="expired", updated_at=now, owner="", result=None)
            )
            row = (
                await conn.execute(
                    select(jobs)
                    .where(
                        jobs.c.status.not_in(TERMINAL),
                        jobs.c.lease_until <= now,
                        jobs.c.deadline > now,
                    )
                    .order_by(jobs.c.created_at)
                    .limit(1)
                )
            ).first()
            if not row:
                return None
            # Compare-and-set: only one worker can acquire this lease.
            changed = await conn.execute(
                update(jobs)
                .where(
                    jobs.c.tenant_id == row.tenant_id,
                    jobs.c.job_id == row.job_id,
                    jobs.c.status.not_in(TERMINAL),
                    jobs.c.lease_until <= now,
                )
                .values(
                    owner=owner, status="planning", updated_at=now, lease_until=now + lease_seconds
                )
            )
            if not changed.rowcount:
                return None
            return _load(
                (
                    await conn.execute(
                        select(jobs).where(
                            jobs.c.tenant_id == row.tenant_id,
                            jobs.c.job_id == row.job_id,
                        )
                    )
                ).one()
            )

    async def touch(
        self,
        scope: TenantScope,
        job_id: str,
        owner: str,
        status: str,
        progress: dict[str, Any],
        lease_seconds: float = 30,
    ) -> bool:
        now = time.time()
        async with self.engine.begin() as conn:
            res = await conn.execute(
                update(jobs)
                .where(
                    jobs.c.tenant_id == scope.tenant_id,
                    jobs.c.job_id == job_id,
                    jobs.c.owner == owner,
                    jobs.c.status.not_in(TERMINAL),
                    jobs.c.deadline > now,
                    jobs.c.lease_until > now,
                )
                .values(
                    status=status,
                    progress=json.dumps(progress),
                    updated_at=now,
                    lease_until=now + lease_seconds,
                )
            )
            return bool(res.rowcount)

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
    ) -> bool:
        if status not in TERMINAL:
            raise ValueError("Completion requires a terminal status")
        # Completion payloads are produced only by the verified API workflow.
        if result and "poem" in result and not (result.get("dat") and result.get("dat_luat")):
            raise ValueError("Unverified poem cannot be persisted")
        if result and result_status not in (200, 422):
            raise ValueError("Invalid result status")
        now = time.time()
        async with self.engine.begin() as conn:
            res = await conn.execute(
                update(jobs)
                .where(
                    jobs.c.tenant_id == scope.tenant_id,
                    jobs.c.job_id == job_id,
                    jobs.c.owner == owner,
                    jobs.c.status.not_in(TERMINAL),
                    jobs.c.deadline > now,
                    jobs.c.lease_until > now,
                )
                .values(
                    status=status,
                    result=json.dumps(result, ensure_ascii=False) if result else None,
                    result_status=result_status,
                    error=error,
                    updated_at=now,
                    owner="",
                    lease_until=0,
                )
            )
            if res.rowcount and result:
                # Job completion and conversation history commit together.
                row = (
                    await conn.execute(
                        select(jobs.c.payload).where(
                            jobs.c.tenant_id == scope.tenant_id,
                            jobs.c.job_id == job_id,
                        )
                    )
                ).one()
                payload = json.loads(row.payload)
                session = payload.get("session_id")
                if session:
                    locked = await conn.execute(
                        update(hoi_thoai)
                        .where(
                            hoi_thoai.c.tenant_id == scope.tenant_id,
                            hoi_thoai.c.conversation_id == session,
                        )
                        .values(cap_nhat_luc=now)
                    )
                    if locked.rowcount:
                        number = int(
                            await conn.scalar(
                                select(func.coalesce(func.max(tin_nhan.c.thu_tu), -1) + 1).where(
                                    tin_nhan.c.tenant_id == scope.tenant_id,
                                    tin_nhan.c.session_id == session,
                                )
                            )
                            or 0
                        )
                        messages = [Message(role=Role.USER, content=payload["yeu_cau"])]
                        answer = result.get("poem", result.get("cau_hoi", ""))
                        if answer:
                            messages.append(Message(role=Role.ASSISTANT, content=answer))
                        for offset, message in enumerate(messages):
                            await conn.execute(
                                insert(tin_nhan).values(
                                    tenant_id=scope.tenant_id,
                                    session_id=session,
                                    thu_tu=number + offset,
                                    noi_dung=message.model_dump_json(),
                                )
                            )
                        await conn.execute(
                            update(hoi_thoai)
                            .where(
                                hoi_thoai.c.tenant_id == scope.tenant_id,
                                hoi_thoai.c.conversation_id == session,
                                hoi_thoai.c.tieu_de == "",
                            )
                            .values(tieu_de=tieu_de_tu_cau(payload["yeu_cau"]))
                        )
            return bool(res.rowcount)

    async def cleanup(self, ttl_seconds: float = 86400) -> None:
        async with self.engine.begin() as conn:
            await conn.execute(
                delete(jobs).where(
                    jobs.c.status.in_(TERMINAL),
                    jobs.c.updated_at < time.time() - ttl_seconds,
                )
            )
