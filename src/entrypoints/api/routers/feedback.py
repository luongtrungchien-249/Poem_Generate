import uuid
from datetime import datetime

from fastapi import APIRouter, Depends

from contracts.feedback import FeedbackRecord, FeedbackRequest
from entrypoints.api.deps import AppContainer, get_container

router = APIRouter(prefix="/v1/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackRecord)
async def submit_feedback(
    req: FeedbackRequest,
    app_container: AppContainer = Depends(get_container),
):
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
    await app_container.relational_repo.save_feedback(record)
    return record


@router.get("", response_model=list[FeedbackRecord])
async def list_feedbacks(
    limit: int = 50,
    app_container: AppContainer = Depends(get_container),
):
    return await app_container.relational_repo.get_feedbacks(limit=limit)
