"""Lưu một lượt hỏi–đáp vào hội thoại.

VÌ SAO LÀ MỘT HÀM DÙNG CHUNG, KHÔNG PHẢI VÀI DÒNG LẶP LẠI Ở TỪNG ROUTER:

Một lượt hội thoại cần ba việc xảy ra cùng nhau — ghi câu hỏi, ghi câu trả lời,
và đặt tiêu đề nếu hội thoại còn trống tên. Rải ba việc đó ra từng router thì mỗi
đường sinh nội dung mới (thơ, chat, và bất kỳ thứ gì thêm sau này) phải nhớ làm đủ
cả ba, và đường nào quên sẽ hỏng theo cách rất khó thấy: người dùng vẫn nhận được
câu trả lời, chỉ là mở lại hội thoại thì nó không còn ở đó.

Đó chính là lỗi đã tồn tại trước ngày 21/09/2026: `/v1/poem` không lưu gì cả, nên
mọi bài thơ biến mất khi tải lại trang — trong khi `/v1/chat` thì lưu.
"""

from __future__ import annotations

from application.ports.repositories import RelationalRepository
from contracts.chat import Message, Role
from domain.conversation.tenant import TenantScope

DAI_TOI_DA_TIEU_DE = 60


def tieu_de_tu_cau(cau: str) -> str:
    """Rút tiêu đề từ câu đầu tiên của người dùng.

    Cắt theo TỪ chứ không theo ký tự: cắt giữa một từ tiếng Việt có thể làm mất
    dấu thanh và tạo ra một từ khác hẳn.
    """
    s = " ".join(cau.split())
    if len(s) <= DAI_TOI_DA_TIEU_DE:
        return s
    cat = s[:DAI_TOI_DA_TIEU_DE].rsplit(" ", 1)[0]
    return f"{cat or s[:DAI_TOI_DA_TIEU_DE]}…"


async def luu_luot(
    kho: RelationalRepository,
    scope: TenantScope,
    conversation_id: str | None,
    *,
    cau_hoi: str,
    tra_loi: str,
) -> None:
    """Ghi một lượt. Không có `conversation_id` thì không ghi gì.

    Trả lời rỗng vẫn ghi câu hỏi: một yêu cầu bị từ chối (thơ không đạt luật, rào
    chắn chặn) vẫn là một phần của lịch sử, và giấu nó đi sẽ làm người dùng mở lại
    hội thoại và không hiểu vì sao có khoảng trống.
    """
    if not conversation_id:
        return

    await kho.save_message(scope, conversation_id, Message(role=Role.USER, content=cau_hoi))
    if tra_loi:
        await kho.save_message(
            scope, conversation_id, Message(role=Role.ASSISTANT, content=tra_loi)
        )
    # Sau khi ghi, không phải trước: hội thoại chỉ đáng có tên khi đã có nội dung.
    await kho.dat_tieu_de_neu_trong(scope, conversation_id, tieu_de_tu_cau(cau_hoi))
