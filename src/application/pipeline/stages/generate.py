import json
import time
from collections.abc import Callable

from application.ports.llm import (
    AssistantMessage,
    CallContext,
    LlmMessage,
    LlmPort,
    ToolCall,
    ToolMessage,
)
from application.ports.rate_limit import RateLimitPort
from application.ports.tools import ToolPort
from application.prompting.context import ContextEnvelope
from domain.common.errors import BotError, BudgetExceeded, UpstreamTimeout
from domain.common.result import Err, Ok, Result


async def generate_react_loop(
    envelope: ContextEnvelope,
    llm: LlmPort,
    tools: ToolPort,
    rate_limiter: RateLimitPort,
    ctx: CallContext,
    max_iterations: int = 5,
    timeout_sec: float = 30.0,
    should_stop_hook: Callable[[], bool] | None = None,
    default_model: str = "gpt-4o-mini",
    la_ban_nhap: Callable[[str], bool] | None = None,
) -> Result[str, BotError]:
    """Executes ReAct reasoning loop with 7 numbered hard guards.

    `la_ban_nhap` — chỉ đường sinh thơ truyền (Plan_PoeTone GĐ3.4). Đo 26/09/2026:
    35/160 bài trượt ở baseline có "bản nháp" CHỈ MỘT DÒNG. Kịch bản: mô hình đưa bài
    thơ vào THAM SỐ của tool `kiem_tra_tho`, nhận kết quả, rồi kết thúc bằng một câu
    kiểu "Bài thơ đã đạt yêu cầu." — và vòng này trả đúng câu đó. Khi có hàm này,
    vòng nhớ văn bản GẦN NHẤT thoả nó (từ lời trả lời hoặc từ tham số gọi tool) và
    trả văn bản ấy khi lời cuối không thoả. Không nới gì cả: kết quả vẫn phải qua
    cổng kiểm như mọi bản nháp khác.
    """
    start_time = time.monotonic()
    current_messages: list[LlmMessage] = list(envelope.messages)
    last_text = ""
    ban_nhap_gan_nhat = ""

    def _ket(van_ban: str) -> str:
        if la_ban_nhap is None or la_ban_nhap(van_ban) or not ban_nhap_gan_nhat:
            return van_ban
        return ban_nhap_gan_nhat

    # GUARD 1: Hard iteration cap
    for iteration in range(1, max_iterations + 1):
        # GUARD 3: Monotonic deadline
        if time.monotonic() - start_time > timeout_sec:
            if last_text:
                return Ok(f"{last_text}\n[Lưu ý: Phản hồi bị cắt ngắn do vượt quá thời gian xử lý]")
            return Err(UpstreamTimeout(upstream="react_loop", timeout_sec=timeout_sec))

        # GUARD 4: Re-check daily budget on every single iteration
        within_budget = await rate_limiter.within_daily_budget(ctx.scope)
        if not within_budget:
            return Err(BudgetExceeded(scope_name=ctx.scope.thread_id, limit=0, current=0))

        # GUARD 6: User cancellation / graceful stop flag
        if should_stop_hook and should_stop_hook():
            if last_text:
                return Ok(last_text)
            return Ok("Yêu cầu đã bị hủy bởi người dùng.")

        # Architectural Rule: Final iteration does NOT receive tools to force synthesis
        available_tools = tools.specs() if iteration < max_iterations else ()

        reply_res = await llm.reply(
            messages=tuple(current_messages),
            tools=available_tools,
            ctx=ctx,
            model=default_model,
        )

        # So khớp tagged union bằng `isinstance`, đúng quy ước của dự án: nó thu
        # hẹp kiểu ở CẢ HAI nhánh, còn TypeGuard (`is_ok`/`is_err`) chỉ thu hẹp ở
        # nhánh đúng nên dòng lấy `.value` phía sau vẫn không được kiểm kiểu.
        if isinstance(reply_res, Err):
            return Err(reply_res.error)

        reply = reply_res.value
        last_text = reply.text
        if la_ban_nhap is not None:
            for ung_vien in (reply.text, *_chuoi_trong_tham_so(reply.tool_calls)):
                if la_ban_nhap(ung_vien):
                    ban_nhap_gan_nhat = ung_vien

        # If model did not emit tool calls, reasoning is complete
        if not reply.tool_calls:
            # GUARD 7: Warn once if answering without consulting docs
            return Ok(_ket(reply.text))

        # Append assistant turn with tool calls
        current_messages.append(AssistantMessage(content=reply.text, tool_calls=reply.tool_calls))

        # Execute tools concurrently
        tool_results = await tools.call_many(reply.tool_calls, ctx)

        # Architectural Rule: Tool results MUST be placed in ToolMessage, NEVER into system or user turn
        for tr in tool_results:
            current_messages.append(ToolMessage(tool_call_id=tr.call_id, content=tr.content))

    if la_ban_nhap is not None and ban_nhap_gan_nhat:
        return Ok(_ket(last_text))
    return Ok(last_text or "Đã hoàn thành các bước suy luận.")


def _chuoi_trong_tham_so(tool_calls: tuple[ToolCall, ...]) -> list[str]:
    """Mọi giá trị chuỗi trong tham số JSON của các lượt gọi tool."""
    ra: list[str] = []
    for tc in tool_calls:
        try:
            tham_so = json.loads(tc.arguments or "{}")
        except json.JSONDecodeError:
            continue
        if isinstance(tham_so, dict):
            ra.extend(v for v in tham_so.values() if isinstance(v, str))
    return ra
