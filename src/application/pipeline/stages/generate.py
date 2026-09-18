import time
from collections.abc import Callable

from application.ports.llm import (
    AssistantMessage,
    CallContext,
    LlmMessage,
    LlmPort,
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
) -> Result[str, BotError]:
    """Executes ReAct reasoning loop with 7 numbered hard guards."""
    start_time = time.monotonic()
    current_messages: list[LlmMessage] = list(envelope.messages)
    last_text = ""

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

        # If model did not emit tool calls, reasoning is complete
        if not reply.tool_calls:
            # GUARD 7: Warn once if answering without consulting docs
            return Ok(reply.text)

        # Append assistant turn with tool calls
        current_messages.append(AssistantMessage(content=reply.text, tool_calls=reply.tool_calls))

        # Execute tools concurrently
        tool_results = await tools.call_many(reply.tool_calls, ctx)

        # Architectural Rule: Tool results MUST be placed in ToolMessage, NEVER into system or user turn
        for tr in tool_results:
            current_messages.append(ToolMessage(tool_call_id=tr.call_id, content=tr.content))

    return Ok(last_text or "Đã hoàn thành các bước suy luận.")
