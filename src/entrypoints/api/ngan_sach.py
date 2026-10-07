"""Chốt trần ngân sách ngày THEO TENANT, dùng chung cho mọi đường tiêu tiền.

════ VÌ SAO CẦN CHỐT NÀY, DÙ ĐÃ CÓ `RateLimitMiddleware` ════

`RateLimitMiddleware` là một gàu token đếm SỐ REQUEST. Nó chặn tần suất, không
chặn tiền: 100 request với `max_tokens` lớn tốn hơn hẳn 10.000 request nhỏ, mà
gàu token thấy hai thứ đó như nhau.

════ VÌ SAO KHÓA THEO TENANT, KHÔNG THEO THREAD ════

`within_daily_budget` khoá theo `platform:thread_id`. Đường thơ trước ngày
21/09/2026 truyền `thread_id = session_id or trace_id` — và `trace_id` là DUY
NHẤT cho mỗi request. Nghĩa là mỗi yêu cầu không kèm `session_id` tự mở một
ngăn ngân sách riêng, đếm lên 1, rồi không bao giờ chạm trần. Trần ngân sách tồn
tại trên giấy nhưng không chặn được gì.

Khoá theo tenant thì người gọi không tự tách ngăn được: tenant đến từ khoá API,
không từ thân request.

Chốt này là BỔ SUNG, không thay thế các lần kiểm theo thread nằm trong pipeline
sinh thơ — hai lớp đo hai thứ khác nhau và cùng cần.
"""

from __future__ import annotations

from fastapi import HTTPException

from application.ports.rate_limit import RateLimitPort
from domain.conversation.thread import ThreadScope


def pham_vi_ngan_sach(tenant_id: str) -> ThreadScope:
    """Ngăn ngân sách của một tenant.

    Tiền tố `ngansach:` tách hẳn khoá này khỏi các khoá đếm theo thread, để một
    hội thoại tình cờ mang id trùng tên tenant không ăn vào cùng một ngăn.
    """
    return ThreadScope(platform="web", thread_id=f"ngansach:{tenant_id}")


async def chan_neu_het_ngan_sach(rate_limiter: RateLimitPort, tenant_id: str) -> None:
    """429 khi tenant đã tiêu hết hạn mức ngày.

    429 chứ không phải 402: đây là hạn mức theo NGÀY, sang ngày mai là hết hạn
    chế. 402 nói rằng cần trả tiền mới đi tiếp được, không đúng với thứ đang xảy ra.
    """
    if not await rate_limiter.within_daily_budget(pham_vi_ngan_sach(tenant_id)):
        raise HTTPException(
            status_code=429,
            detail="Đã dùng hết hạn mức của ngày hôm nay. Vui lòng thử lại vào ngày mai.",
        )
