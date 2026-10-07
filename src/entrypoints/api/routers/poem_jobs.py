"""Job admission/status/events. Disconnecting SSE never cancels a job."""

import asyncio
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from application.ports.poem_jobs import TERMINAL, JobConflict, JobLimit, PoemJob, PoemJobStore
from contracts.poem import PoemRequest
from contracts.poem_jobs import PoemJobResponse
from domain.guardrails.input import check_forbidden_topics, check_input_length, detect_injection
from entrypoints.api.deps import AppContainer, get_container
from entrypoints.api.middleware.auth import tenant_scope_cua

router = APIRouter(prefix="/v1/poem/jobs", tags=["Poem jobs"])


def public_job(job: PoemJob) -> PoemJobResponse:
    return PoemJobResponse(
        job_id=job.job_id,
        status=job.status,
        conversation_id=job.payload.get("session_id"),
        created_at=job.created_at,
        updated_at=job.updated_at,
        deadline=job.deadline,
        model=job.model,
        provider=job.provider,
        progress=job.progress,
        result=job.result,
        result_status=job.result_status,
        error=job.error,
    )


def store(container: AppContainer) -> PoemJobStore:
    if container.poem_jobs is None:
        raise HTTPException(503, "Kho job chưa được cấu hình.")
    return container.poem_jobs


@router.post("", status_code=202, response_model=PoemJobResponse)
async def create_job(
    req: PoemRequest,
    request: Request,
    container: AppContainer = Depends(get_container),
    idempotency_key: str | None = Header(None, min_length=1, max_length=128),
) -> PoemJobResponse:
    if not check_input_length(req.yeu_cau).is_valid or detect_injection(req.yeu_cau).is_injection:
        raise HTTPException(400, "Yêu cầu không hợp lệ.")
    if check_forbidden_topics(req.yeu_cau).muc == "BLOCK":
        raise HTTPException(400, "Chủ đề không được hỗ trợ.")
    tenant = tenant_scope_cua(request)
    if (
        req.session_id
        and await container.relational_repo.lay_hoi_thoai(tenant, req.session_id) is None
    ):
        raise HTTPException(404, "Không tìm thấy hội thoại.")
    cfg = container.settings.poem_jobs
    try:
        job = await store(container).create(
            tenant,
            req.model_dump(),
            idempotency_key or uuid.uuid4().hex,
            model=container.default_model,
            provider=container.settings.llm.default_provider,
            deadline_seconds=cfg.deadline_seconds,
            active_limit=cfg.active_limit,
        )
    except JobConflict as exc:
        raise HTTPException(409, str(exc)) from exc
    except JobLimit as exc:
        raise HTTPException(429, str(exc)) from exc
    return public_job(job)


@router.get("", response_model=list[PoemJobResponse])
async def active_jobs(
    request: Request,
    conversation_id: str = Query(..., max_length=256),
    container: AppContainer = Depends(get_container),
) -> list[PoemJobResponse]:
    return [
        public_job(job)
        for job in await store(container).list_active(tenant_scope_cua(request), conversation_id)
    ]


@router.get("/{job_id}", response_model=PoemJobResponse)
async def get_job(
    job_id: str, request: Request, container: AppContainer = Depends(get_container)
) -> PoemJobResponse:
    job = await store(container).get(tenant_scope_cua(request), job_id)
    if job is None:
        raise HTTPException(404, "Không tìm thấy job.")
    return public_job(job)


@router.delete("/{job_id}", response_model=PoemJobResponse)
async def cancel_job(
    job_id: str, request: Request, container: AppContainer = Depends(get_container)
) -> PoemJobResponse:
    job = await store(container).cancel(tenant_scope_cua(request), job_id)
    if job is None:
        raise HTTPException(404, "Không tìm thấy job.")
    return public_job(job)


@router.get("/{job_id}/events")
async def job_events(
    job_id: str, request: Request, container: AppContainer = Depends(get_container)
) -> StreamingResponse:
    tenant = tenant_scope_cua(request)
    if await store(container).get(tenant, job_id) is None:
        raise HTTPException(404, "Không tìm thấy job.")

    async def events():
        last = None
        while not await request.is_disconnected():
            job = await store(container).get(tenant, job_id)
            if job is None:
                return
            data = public_job(job).model_dump_json()
            terminal = job.status in TERMINAL
            if data != last or terminal:
                event = "done" if terminal else "progress"
                yield f"id: {job.updated_at}\nevent: {event}\ndata: {data}\n\n"
                last = data
            else:
                yield ": heartbeat\n\n"
            if terminal:
                return
            await asyncio.sleep(1)

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        },
    )
