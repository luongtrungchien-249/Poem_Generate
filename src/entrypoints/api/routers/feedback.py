import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Request

from contracts.feedback import FeedbackRecord, FeedbackRequest
from entrypoints.api.deps import AppContainer, get_container
from entrypoints.api.middleware.auth import tenant_scope_cua

router = APIRouter(prefix="/v1/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackRecord)
async def submit_feedback(
    req: FeedbackRequest,
    raw_request: Request,
    app_container: AppContainer = Depends(get_container),
):
    scope = tenant_scope_cua(raw_request)
    record = FeedbackRecord(
        id=f"fb-{uuid.uuid4().hex[:10]}",
        trace_id=req.trace_id,
        rating=req.rating,
        comment=req.comment,
        tags=req.tags,
        user_id=req.user_id,
        tenant_id=req.tenant_id,
        created_at=datetime.utcnow(),
    )
    await app_container.relational_repo.save_feedback(scope, record)
    return record


@router.get("", response_model=list[FeedbackRecord])
async def list_feedbacks(
    raw_request: Request,
    limit: int = 50,
    app_container: AppContainer = Depends(get_container),
):
    # Chỉ trả phản hồi CỦA TENANT NÀY. Bản trước trả toàn bộ bảng.
    return await app_container.relational_repo.get_feedbacks(
        tenant_scope_cua(raw_request), limit=limit
    )
