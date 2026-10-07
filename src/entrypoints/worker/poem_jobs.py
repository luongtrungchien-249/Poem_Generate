"""Durable SQL worker. Run separately in production; lifespan embeds it in dev."""

import asyncio
import contextlib
import json
import logging
import time
import uuid
from dataclasses import replace

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from application.conversation import luu_luot
from application.poetry.budget import JobBudgetLlm
from application.poetry.tools import PoetryTools
from application.ports.poem_jobs import PoemJob
from bootstrap.container import AppContainer, build_container, close_container
from bootstrap.model_validation import validate_remote_model
from bootstrap.settings import get_settings
from contracts.poem import PoemRequest
from domain.conversation.tenant import TenantScope
from entrypoints.api.routers.poem import execute_poem

logger = logging.getLogger("poem.worker")


async def run_job(container: AppContainer, job: PoemJob) -> None:
    repo = container.poem_jobs
    assert repo is not None
    cfg = container.settings.poem_jobs
    tenant = TenantScope(job.tenant_id)
    state = {"status": "planning", "progress": {}}

    async def progress(status: str, details: dict) -> None:
        state["status"] = status
        state["progress"] = details
        if not await repo.touch(tenant, job.job_id, job.owner, status, details, cfg.lease_seconds):
            raise asyncio.CancelledError

    request = PoemRequest(**job.payload)
    if (
        job.model != container.default_model
        or job.provider != container.settings.llm.default_provider
    ):
        await repo.finish(
            tenant,
            job.job_id,
            job.owner,
            status="failed",
            error="Cấu hình model đã đổi; vui lòng tạo job mới.",
        )
        return
    job_container = replace(
        container,
        tools=PoetryTools(container.tools),
        chat_llm=JobBudgetLlm(
            container.chat_llm,
            container.rate_limiter,
            job.tenant_id,
            cfg.max_model_calls,
        ),
    )
    task = asyncio.create_task(
        execute_poem(
            request,
            job_container,
            tenant,
            job.job_id,
            progress_hook=progress,
            save_history=False,
        )
    )

    async def heartbeat() -> None:
        while not task.done():
            await asyncio.sleep(min(1, cfg.lease_seconds / 3))
            try:
                alive = await repo.touch(
                    tenant,
                    job.job_id,
                    job.owner,
                    state["status"],
                    state["progress"],
                    cfg.lease_seconds,
                )
            except Exception:
                # Stop spending if ownership cannot be renewed. The durable
                # lease allows another process to recover when SQL returns.
                task.cancel()
                return
            if not alive:
                task.cancel()
                return

    beat = asyncio.create_task(heartbeat())
    try:
        async with asyncio.timeout(max(0.01, job.deadline - time.time())):
            outcome = await task
        if isinstance(outcome, JSONResponse):
            body, code = json.loads(outcome.body), outcome.status_code
        else:
            body, code = outcome.model_dump(mode="json"), 200
        done = await repo.finish(
            tenant,
            job.job_id,
            job.owner,
            status="completed" if code == 200 else "failed",
            result=body,
            result_status=code,
        )
        # Memory storage is development-only. SQL storage writes history in the
        # same transaction as completion; it must not be saved twice here.
        if done and container.settings.storage.kind == "in_memory":
            await luu_luot(
                container.relational_repo,
                tenant,
                request.session_id,
                cau_hoi=request.yeu_cau,
                tra_loi=body.get("poem", body.get("cau_hoi", "")),
            )
    except TimeoutError:
        # get() marks expired by the same deadline used for the timeout.
        await repo.get(tenant, job.job_id)
    except asyncio.CancelledError:
        task.cancel()
        if asyncio.current_task().cancelling():
            raise
    except HTTPException as exc:
        await repo.finish(
            tenant,
            job.job_id,
            job.owner,
            status="failed",
            error=f"Yêu cầu bị từ chối (HTTP {exc.status_code}).",
        )
    except Exception as exc:
        logger.error("Job %s failed (%s)", job.job_id, type(exc).__name__)
        await repo.finish(
            tenant, job.job_id, job.owner, status="failed", error="Lỗi xử lý job; vui lòng thử lại."
        )
    finally:
        beat.cancel()
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await beat
        with contextlib.suppress(asyncio.CancelledError, Exception):
            await task


async def worker_loop(container: AppContainer) -> None:
    repo = container.poem_jobs
    assert repo is not None
    while True:
        try:
            await repo.cleanup(container.settings.poem_jobs.ttl_seconds)
            job = await repo.claim(uuid.uuid4().hex, container.settings.poem_jobs.lease_seconds)
            if job:
                try:
                    await run_job(container, job)
                except asyncio.CancelledError:
                    # Cancellation due to fenced lease/tenant cancel is local.
                    # Process shutdown cancellation must propagate.
                    if asyncio.current_task().cancelling():
                        raise
            else:
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("Queue unavailable (%s)", type(exc).__name__)
            await asyncio.sleep(2)


async def main() -> None:
    from adapters.persistence.sql.engine import tao_bang
    from adapters.persistence.sql.poem_jobs import SqlPoemJobStore

    settings = get_settings()
    await validate_remote_model(settings)
    container = build_container(settings)
    assert isinstance(container.poem_jobs, SqlPoemJobStore)
    if settings.env != "dev" and settings.storage.kind == "in_memory":
        raise ValueError("Worker production cần storage SQL dùng chung.")
    await tao_bang(container.poem_jobs.engine)
    try:
        await worker_loop(container)
    finally:
        await close_container(container)


if __name__ == "__main__":
    asyncio.run(main())
