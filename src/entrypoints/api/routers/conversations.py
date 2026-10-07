"""§11 · §15 `AI_LLM_Chat_Web_UI_Plan.md` — quản lý hội thoại và danh mục model.

MỌI ĐƯỜNG Ở ĐÂY ĐỀU THEO TENANT CỦA KHOÁ API, không theo tham số người gọi gửi
lên. Đó là điều tài liệu kế hoạch KHÔNG nhắc tới: §15 có cột `user_id` nhưng §28
không có mục xác thực nào, và một `user_id` do client tự khai thì mọi cô lập ở
tầng dưới đều vô nghĩa.

Vì sao `conversation_id` do MÁY CHỦ sinh: cho client tự đặt thì hai người dùng
khác tenant vẫn đoán trúng id của nhau được. Cô lập tenant chặn được việc ĐỌC,
nhưng đoán trúng vẫn là một kênh dò thông tin.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from application.conversation.cursor import encode_cursor
from contracts.conversation import (
    Conversation,
    ConversationCreate,
    ConversationDetail,
    ConversationUpdate,
    ModelInfo,
)
from entrypoints.api.deps import AppContainer, get_container
from entrypoints.api.middleware.auth import tenant_scope_cua

router = APIRouter(prefix="/v1", tags=["Conversations"])


@router.post("/conversations", response_model=Conversation)
async def tao_hoi_thoai(
    req: ConversationCreate,
    raw_request: Request,
    app_container: AppContainer = Depends(get_container),
) -> Conversation:
    return await app_container.relational_repo.tao_hoi_thoai(
        tenant_scope_cua(raw_request), tieu_de=req.tieu_de, model=req.model
    )


@router.get("/conversations", response_model=list[Conversation])
async def danh_sach_hoi_thoai(
    raw_request: Request,
    response: Response,
    limit: int = 50,
    q: str = Query("", max_length=512),
    cursor: str | None = Query(None, max_length=1024),
    app_container: AppContainer = Depends(get_container),
) -> list[Conversation]:
    # Không trả kèm tin nhắn: danh sách sidebar mà kéo theo toàn bộ nội dung từng
    # cuộc là một truy vấn nặng dần theo lịch sử người dùng.
    size = min(max(limit, 1), 200)
    try:
        rows = await app_container.relational_repo.danh_sach_hoi_thoai(
            tenant_scope_cua(raw_request), limit=size + 1, q=q, cursor=cursor
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Cursor không hợp lệ.") from exc
    if len(rows) > size:
        last = rows[size - 1]
        response.headers["x-next-cursor"] = last._page_cursor or encode_cursor(
            last.cap_nhat_luc.timestamp(), last.conversation_id
        )
    return rows[:size]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def lay_hoi_thoai(
    conversation_id: str,
    raw_request: Request,
    limit_tin_nhan: int = 100,
    app_container: AppContainer = Depends(get_container),
) -> ConversationDetail:
    scope = tenant_scope_cua(raw_request)
    hoi_thoai = await app_container.relational_repo.lay_hoi_thoai(scope, conversation_id)
    if hoi_thoai is None:
        # 404 cho cả "không tồn tại" lẫn "thuộc tenant khác". Phân biệt hai ca đó
        # là nói cho người dò biết id nào có thật.
        raise HTTPException(status_code=404, detail="Không tìm thấy hội thoại.")

    tin_nhan = await app_container.relational_repo.get_messages(
        scope, conversation_id, limit=min(max(limit_tin_nhan, 1), 500)
    )
    return ConversationDetail(
        **hoi_thoai.model_dump(),
        tin_nhan=[m.model_dump() for m in tin_nhan],
    )


@router.patch("/conversations/{conversation_id}", response_model=Conversation)
async def sua_hoi_thoai(
    conversation_id: str,
    req: ConversationUpdate,
    raw_request: Request,
    app_container: AppContainer = Depends(get_container),
) -> Conversation:
    ra = await app_container.relational_repo.sua_hoi_thoai(
        tenant_scope_cua(raw_request),
        conversation_id,
        tieu_de=req.tieu_de,
        model=req.model,
    )
    if ra is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy hội thoại.")
    return ra


@router.delete("/conversations/{conversation_id}")
async def xoa_hoi_thoai(
    conversation_id: str,
    raw_request: Request,
    app_container: AppContainer = Depends(get_container),
) -> dict[str, bool]:
    # Xoá hội thoại xoá luôn tin nhắn — xem `xoa_hoi_thoai` của kho lưu trữ.
    da_xoa = await app_container.relational_repo.xoa_hoi_thoai(
        tenant_scope_cua(raw_request), conversation_id
    )
    if not da_xoa:
        raise HTTPException(status_code=404, detail="Không tìm thấy hội thoại.")
    return {"da_xoa": True}


@router.get("/models", response_model=list[ModelInfo])
async def danh_sach_model(
    app_container: AppContainer = Depends(get_container),
) -> list[ModelInfo]:
    """§14 — UI chỉ cần tên model, backend tự biết gọi provider nào.

    Dữ liệu lấy thẳng từ `configs/models.yaml` qua `ModelRouter`, không chép tay:
    một danh sách chép tay sẽ lệch khỏi cấu hình thật, và UI sẽ mời người dùng
    chọn một model mà backend không định tuyến được.

    KHÔNG phơi giá tiền: giá là chuyện vận hành, không phải thứ để trình bày cho
    người dùng cuối, và nó đổi theo hợp đồng với nhà cung cấp.
    """
    return [
        ModelInfo(
            ten=ten,
            provider=str(cau_hinh.get("provider", "")),
            tier=str(cau_hinh.get("tier", "")),
            context_window=int(cau_hinh.get("context_window", 0)),
            max_output_tokens=int(cau_hinh.get("max_output_tokens", 0)),
        )
        for ten, cau_hinh in sorted(app_container.router.models.items())
    ]
