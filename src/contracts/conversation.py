"""Hợp đồng HTTP cho quản lý hội thoại — §15 `AI_LLM_Chat_Web_UI_Plan.md`.

`conversation_id` do MÁY CHỦ sinh, không nhận từ client. Cho client tự đặt id thì
hai người dùng khác tenant vẫn có thể đoán trúng id của nhau — và dù cô lập tenant
chặn được việc đọc, việc đoán trúng vẫn là một kênh dò thông tin.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    """Tạo hội thoại mới. Mọi trường đều tuỳ chọn — tiêu đề có thể đặt sau."""

    tieu_de: str = Field("", max_length=512)
    model: str = Field("", max_length=128)


class ConversationUpdate(BaseModel):
    tieu_de: str | None = Field(None, max_length=512)
    model: str | None = Field(None, max_length=128)


class Conversation(BaseModel):
    conversation_id: str
    tieu_de: str
    model: str
    tao_luc: datetime
    cap_nhat_luc: datetime
    so_tin_nhan: int = 0


class ConversationDetail(Conversation):
    """Hội thoại kèm tin nhắn. Tách riêng khỏi `Conversation` vì danh sách hội
    thoại KHÔNG được kéo theo toàn bộ tin nhắn của từng cuộc."""

    tin_nhan: list[dict] = Field(default_factory=list)


class ModelInfo(BaseModel):
    """§14 — UI chỉ cần tên model; backend tự biết gọi provider nào."""

    ten: str
    provider: str
    tier: str = ""
    context_window: int = 0
    max_output_tokens: int = 0
