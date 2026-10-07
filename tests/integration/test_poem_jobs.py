import asyncio
import time

import pytest
from sqlalchemy import update

from adapters.persistence.sql.bang import poem_jobs
from adapters.persistence.sql.engine import tao_bang, tao_engine
from adapters.persistence.sql.poem_jobs import SqlPoemJobStore
from adapters.persistence.sql.relational import SqlRelationalRepository
from application.ports.poem_jobs import JobConflict, JobLimit
from domain.conversation.tenant import TenantScope


@pytest.fixture
async def stores(isolated_sql_dsn):
    engines = [tao_engine(isolated_sql_dsn), tao_engine(isolated_sql_dsn)]
    await tao_bang(engines[0])
    yield [SqlPoemJobStore(engine) for engine in engines]
    for engine in engines:
        await engine.dispose()


async def new(store, key="key", tenant="a", **options):
    return await store.create(
        TenantScope(tenant),
        {"yeu_cau": "quê hương"},
        key,
        model="mock-gpt",
        provider="mock",
        deadline_seconds=300,
        active_limit=2,
        **options,
    )


async def test_idempotency_atomic_across_connections_and_payload_conflict(stores):
    first, second = await asyncio.gather(new(stores[0]), new(stores[1]))
    assert first.job_id == second.job_id
    with pytest.raises(JobConflict):
        await stores[0].create(
            TenantScope("a"),
            {"yeu_cau": "khác"},
            "key",
            model="mock-gpt",
            provider="mock",
            deadline_seconds=300,
            active_limit=2,
        )


async def test_tenant_visibility_cancel_and_admission(stores):
    job = await new(stores[0])
    assert await stores[1].get(TenantScope("b"), job.job_id) is None
    assert await stores[1].cancel(TenantScope("b"), job.job_id) is None
    other = await new(stores[1], "key", "b")
    assert other.job_id != job.job_id
    await new(stores[0], "second")
    with pytest.raises(JobLimit):
        await new(stores[0], "third")
    assert (await stores[1].cancel(TenantScope("a"), job.job_id)).status == "cancelled"
    await new(stores[0], "third")


async def test_concurrent_admission_cannot_exceed_limit(stores):
    results = await asyncio.gather(
        *(new(stores[i % 2], str(i)) for i in range(5)), return_exceptions=True
    )
    assert sum(not isinstance(r, Exception) for r in results) == 2
    assert sum(isinstance(r, JobLimit) for r in results) == 3


async def test_only_one_worker_claims_and_stale_worker_cannot_finish(stores):
    job = await new(stores[0])
    claims = await asyncio.gather(stores[0].claim("old", 30), stores[1].claim("another", 30))
    claimed = [claim for claim in claims if claim]
    assert len(claimed) == 1
    assert claimed[0].job_id == job.job_id
    async with stores[0].engine.begin() as conn:
        await conn.execute(update(poem_jobs).values(lease_until=time.time() - 1))
    recovered = await stores[1].claim("new", 30)
    assert recovered.job_id == job.job_id
    assert not await stores[0].finish(
        TenantScope("a"), job.job_id, claimed[0].owner, status="completed"
    )
    assert await stores[1].finish(
        TenantScope("a"), job.job_id, "new", status="failed", error="safe"
    )


async def test_cancel_fences_result_and_no_draft_can_be_written(stores):
    job = await new(stores[0])
    await stores[0].claim("worker", 30)
    with pytest.raises(ValueError):
        await stores[0].finish(
            TenantScope("a"),
            job.job_id,
            "worker",
            status="completed",
            result={"poem": "invalid", "dat": False},
            result_status=200,
        )
    await stores[1].cancel(TenantScope("a"), job.job_id)
    assert not await stores[0].finish(TenantScope("a"), job.job_id, "worker", status="completed")
    assert (await stores[0].get(TenantScope("a"), job.job_id)).result is None


async def test_deadline_ttl_and_persistence(stores):
    job = await new(stores[0])
    async with stores[0].engine.begin() as conn:
        await conn.execute(update(poem_jobs).values(deadline=time.time() - 1))
    assert await stores[1].claim("worker", 30) is None
    assert (await stores[1].get(TenantScope("a"), job.job_id)).status == "expired"
    async with stores[0].engine.begin() as conn:
        await conn.execute(update(poem_jobs).values(updated_at=0))
    await stores[1].cleanup(10)
    assert await stores[0].get(TenantScope("a"), job.job_id) is None


async def test_history_and_completion_are_saved_once(stores):
    relational = SqlRelationalRepository(stores[0].engine)
    tenant = TenantScope("a")
    conversation = await relational.tao_hoi_thoai(tenant)
    payload = {"yeu_cau": "thơ", "session_id": conversation.conversation_id}
    job = await stores[0].create(
        tenant,
        payload,
        "key",
        model="mock-gpt",
        provider="mock",
        deadline_seconds=300,
        active_limit=2,
    )
    await stores[0].claim("worker", 30)
    outcome = {"can_lam_ro": True, "cau_hoi": "Bạn muốn chủ đề nào?"}
    assert await stores[0].finish(
        tenant, job.job_id, "worker", status="completed", result=outcome, result_status=200
    )
    assert not await stores[0].finish(
        tenant, job.job_id, "worker", status="completed", result=outcome, result_status=200
    )
    messages = await relational.get_messages(tenant, conversation.conversation_id)
    assert len(messages) == 2
    assert messages[1].content == outcome["cau_hoi"]
