import asyncio

from application.ports.channel import ChannelPort
from application.ports.logger import LoggerPort
from domain.conversation.message import OutboundMessage
from domain.conversation.thread import ThreadScope
from domain.policy.output_guard import OutputVerdict, apply_output_guardrails


def start_typing(channel: ChannelPort, scope: ThreadScope, logger: LoggerPort) -> asyncio.Task[None]:
    """Fires typing indicator without blocking. Catches exceptions internally so background task doesn't crash unhandled."""
    async def _run() -> None:
        try:
            await channel.typing(scope)
        except Exception as err:
            logger.warning(f"Typing indicator failed: {err}")

    return asyncio.create_task(_run())


def chuan_bi_phan_hoi(
    raw_text: str,
    user_pii: frozenset[str],
    has_retrieved_knowledge: bool = False,
) -> OutputVerdict:
    """Áp output rails và trả về văn bản CUỐI CÙNG, chưa gửi đi.

    Tách khỏi việc gửi để có một khe cắm ở giữa cho cổng kiểm định thể loại.
    Trước đây hai việc này gộp làm một, nên không có chỗ nào kiểm được đúng chuỗi
    byte sắp ra khỏi hệ thống.

    THỨ TỰ BẮT BUỘC — đừng tối ưu:
        1. output rails (có thể ĐỔI văn bản: che bí mật, che PII)
        2. kiểm định thể loại (phải chạy trên văn bản ĐÃ đổi)
        3. gửi
    Kiểm trước khi che thì bài được kiểm không phải là bài được gửi: một chuỗi bị
    thay bằng [REDACTED_PHONE] là số tiếng của dòng đó đã khác.
    """
    return apply_output_guardrails(
        raw_text=raw_text,
        user_provided_pii=user_pii,
        has_retrieved_knowledge=has_retrieved_knowledge,
    )


async def gui_phan_hoi(
    text: str,
    scope: ThreadScope,
    channel: ChannelPort,
    reply_to_id: str | None = None,
) -> None:
    """Chỉ gửi. Không biến đổi gì thêm — mọi biến đổi đã xong ở bước chuẩn bị."""
    await channel.send(scope, OutboundMessage(text=text, reply_to_id=reply_to_id))


async def send_response(
    raw_text: str,
    scope: ThreadScope,
    channel: ChannelPort,
    user_pii: frozenset[str],
    has_retrieved_knowledge: bool = False,
    reply_to_id: str | None = None,
) -> OutputVerdict:
    """Đường tắt cho phản hồi KHÔNG có ràng buộc thể loại: chuẩn bị rồi gửi luôn.

    Phản hồi CÓ ràng buộc phải đi qua hai hàm trên để cổng kiểm định chen được
    vào giữa.
    """
    verdict = chuan_bi_phan_hoi(raw_text, user_pii, has_retrieved_knowledge)
    await gui_phan_hoi(verdict.text, scope, channel, reply_to_id)
    return verdict
