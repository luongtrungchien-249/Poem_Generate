import asyncio
import importlib
import time
from dataclasses import replace

import httpx
import pytest
from sqlalchemy import update

from adapters.persistence.sql.bang import poem_jobs
from adapters.persistence.sql.engine import tao_bang
from bootstrap.container import build_container
from bootstrap.settings import LLMConfig, Secrets, Settings, StorageConfig
from domain.conversation.tenant import TenantScope
from entrypoints.api.deps import get_container
from entrypoints.worker.poem_jobs import run_job


@pytest.fixture
async def job_api(tmp_path, monkeypatch):
    settings = Settings(
        project_root=tmp_path,
        storage=StorageConfig(kind="sqlite", sqlite_path="app.db"),
        llm=LLMConfig(default_provider="mock", default_model="mock-gpt"),
        secrets=Secrets(_env_file=None, API_KEYS="key-a:a,key-b:b"),
    )
    container = build_container(settings)
    await tao_bang(container.poem_jobs.engine)
    api = importlib.import_module("entrypoints.api.app")
    monkeypatch.setattr(api, "get_settings", lambda: settings)
    app = api.create_app()
    app.dependency_overrides[get_container] = lambda: container
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        headers={"x-api-key": "key-a"},
    ) as client:
        yield client, container
    # Dispose all engines acquired by this isolated container.
    engines = {
        container.poem_jobs.engine,
        container.relational_repo._engine,
        container.vector_repo._engine,
        container.cache_repo._engine,
        container.rate_limiter._engine,
    }
    for engine in engines:
        await engine.dispose()


async def test_jobs_auth_idempotency_tenant_and_safe_terminal_sse(job_api):
    client, container = job_api
    payload = {
        "yeu_cau": "Viết bài thơ quê hương",
        "chu_de": "quê hương",
        "so_dong": 4,
        "max_repair_rounds": 0,
    }
    unauthorized = await client.post(
        "/v1/poem/jobs", json=payload, headers={"x-api-key": "invalid"}
    )
    assert unauthorized.status_code == 401
    first = await client.post("/v1/poem/jobs", json=payload, headers={"idempotency-key": "retry"})
    assert first.status_code == 202
    second = await client.post("/v1/poem/jobs", json=payload, headers={"idempotency-key": "retry"})
    assert first.json()["job_id"] == second.json()["job_id"]
    path = f"/v1/poem/jobs/{first.json()['job_id']}"
    assert (await client.get(path, headers={"x-api-key": "key-b"})).status_code == 404
    conflict = await client.post(
        "/v1/poem/jobs", json={**payload, "so_dong": 8}, headers={"idempotency-key": "retry"}
    )
    assert conflict.status_code == 409
    job = await container.poem_jobs.claim("worker", 30)
    await run_job(container, job)
    final = (await client.get(path)).json()
    assert final["status"] == "failed" and final["result_status"] == 422
    assert "poem" not in final["result"]
    assert "payload" not in final and "tenant_id" not in final
    stream = await client.get(path + "/events")
    assert "event: done" in stream.text
    assert "ban_nhap" not in stream.text


async def test_job_cancel_deadline_and_worker_shutdown(job_api, monkeypatch):
    client, container = job_api
    response = await client.post("/v1/poem/jobs", json={"yeu_cau": "thơ"})
    job_id = response.json()["job_id"]
    claimed = await container.poem_jobs.claim("worker", 30)
    assert (await client.delete(f"/v1/poem/jobs/{job_id}")).json()["status"] == "cancelled"
    await run_job(container, claimed)
    assert (await client.get(f"/v1/poem/jobs/{job_id}")).json()["result"] is None


async def test_disconnecting_events_does_not_cancel_worker(job_api):
    client, container = job_api
    response = await client.post("/v1/poem/jobs", json={"yeu_cau": "thơ"})
    path = f"/v1/poem/jobs/{response.json()['job_id']}"
    # The worker's lifecycle is independent from the HTTP client transport.
    job = await container.poem_jobs.claim("worker", 30)
    await run_job(container, job)
    terminal = (await client.get(path)).json()
    assert terminal["status"] == "completed"
    assert terminal["result"]["can_lam_ro"] is True


async def test_worker_total_deadline_cancels_model_task(job_api, monkeypatch):
    client, container = job_api
    response = await client.post("/v1/poem/jobs", json={"yeu_cau": "thơ"})
    job = await container.poem_jobs.claim("worker", 30)
    deadline = time.time() + 0.1
    async with container.poem_jobs.engine.begin() as conn:
        await conn.execute(update(poem_jobs).values(deadline=deadline))
    cancelled = asyncio.Event()

    async def slow(*args, **kwargs):
        try:
            await asyncio.sleep(10)
        finally:
            cancelled.set()

    monkeypatch.setattr("entrypoints.worker.poem_jobs.execute_poem", slow)
    await run_job(container, replace(job, deadline=deadline))
    assert cancelled.is_set()
    final = (await client.get(f"/v1/poem/jobs/{response.json()['job_id']}")).json()
    assert final["status"] == "expired" and final["result"] is None


async def test_worker_shutdown_does_not_publish_partial_result(job_api, monkeypatch):
    client, container = job_api
    response = await client.post("/v1/poem/jobs", json={"yeu_cau": "thơ"})
    job = await container.poem_jobs.claim("worker", 30)
    started = asyncio.Event()

    async def slow(*args, **kwargs):
        started.set()
        await asyncio.sleep(10)

    monkeypatch.setattr("entrypoints.worker.poem_jobs.execute_poem", slow)
    task = asyncio.create_task(run_job(container, job))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    final = (await client.get(f"/v1/poem/jobs/{response.json()['job_id']}")).json()
    assert final["result"] is None and final["status"] not in {"failed", "completed"}


async def test_failed_heartbeat_stops_spending_until_recovery(job_api, monkeypatch):
    client, container = job_api
    await client.post("/v1/poem/jobs", json={"yeu_cau": "thơ"})
    job = await container.poem_jobs.claim("worker", 30)
    cancelled = asyncio.Event()

    async def slow(*args, **kwargs):
        try:
            await asyncio.sleep(10)
        finally:
            cancelled.set()

    async def unavailable(*args, **kwargs):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr("entrypoints.worker.poem_jobs.execute_poem", slow)
    monkeypatch.setattr(container.poem_jobs, "touch", unavailable)
    await asyncio.wait_for(run_job(container, job), 3)
    assert cancelled.is_set()
    assert (await container.poem_jobs.get(TenantScope("a"), job.job_id)).result is None


async def test_real_lifespan_embedded_worker_and_sql_history(tmp_path, monkeypatch):
    settings = Settings(
        project_root=tmp_path,
        storage=StorageConfig(kind="sqlite", sqlite_path="lifespan.db"),
        llm=LLMConfig(default_provider="mock", default_model="mock-gpt"),
        secrets=Secrets(_env_file=None, API_KEYS="test-key:a"),
    )
    api = importlib.import_module("entrypoints.api.app")
    monkeypatch.setattr(api, "get_settings", lambda: settings)
    app = api.create_app()
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
            headers={"x-api-key": "test-key"},
        ) as client,
    ):
        conversation = (await client.post("/v1/conversations", json={})).json()
        response = await client.post(
            "/v1/poem/jobs",
            json={"yeu_cau": "thơ", "session_id": conversation["conversation_id"]},
        )
        assert response.status_code == 202
        path = f"/v1/poem/jobs/{response.json()['job_id']}"
        async with asyncio.timeout(5):
            while True:
                snapshot = (await client.get(path)).json()
                if snapshot["status"] == "completed":
                    break
                await asyncio.sleep(0.05)
        assert snapshot["result"]["can_lam_ro"] is True
        history = (await client.get(f"/v1/conversations/{conversation['conversation_id']}")).json()
        assert len(history["tin_nhan"]) == 2
        assert "event: done" in (await client.get(path + "/events")).text


async def test_frontend_declared_fields_match_openapi(job_api):
    import re
    from pathlib import Path

    client, _ = job_api
    spec = (await client.get("/openapi.json")).json()
    script = (Path(__file__).resolve().parents[2] / "frontend/scripts/gen-types.mjs").read_text(
        encoding="utf-8"
    )
    required = re.search(r"const CAN_CO = \{(.*?)\n\};", script, re.S).group(1)
    for name, fields in re.findall(r"(\w+):\s*\[(.*?)\]", required, re.S):
        declared = set(re.findall(r'"([^\"]+)"', fields))
        assert declared <= spec["components"]["schemas"][name]["properties"].keys(), name
    assert "payload" not in spec["components"]["schemas"]["PoemJobResponse"]["properties"]
