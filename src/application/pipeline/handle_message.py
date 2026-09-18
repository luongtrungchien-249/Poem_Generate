import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeAlias

from application.pipeline.stages.generate import generate_react_loop
from application.pipeline.stages.respond import send_response, start_typing
from application.ports.channel import ChannelPort
from application.ports.llm import CallContext, LlmPort
from application.ports.logger import LoggerPort
from application.ports.memory import MemoryPort
from application.ports.rate_limit import RateLimitPort, Silent, Warn
from application.ports.tools import ToolPort
from application.prompting.context import assemble_context_envelope
from domain.common.errors import BotError, is_retryable, is_silent
from domain.common.result import Err
from domain.conversation.message import InboundMessage, StoredMessage
from domain.policy.command import (
    Answer,
    AskConfirm,
    DeferredWrite,
    parse_command,
)
from domain.policy.injection import scan_injection
from domain.policy.mention import MentionFound, build_mention_regex, extract_mention


@dataclass(frozen=True, slots=True)
class PipelineDeps:
    """Dependency injection container for a single message pipeline execution."""
    llm: LlmPort
    memory: MemoryPort
    tools: ToolPort
    rate_limiter: RateLimitPort
    channel: ChannelPort
    logger: LoggerPort
    bot_names: tuple[str, ...] = ("bot", "ai", "assistant")
    is_final_attempt: bool = True
    should_stop_hook: Callable[[], bool] | None = None
    default_model: str = "gpt-4o-mini"


@dataclass(frozen=True, slots=True)
class Handled:
    replied: bool


@dataclass(frozen=True, slots=True)
class Failed:
    error: BotError
    replied: bool # Essential flag: separates 'text sent' from 'job retriable'


HandleResult: TypeAlias = Handled | Failed


async def handle_inbound_message(msg: InboundMessage, deps: PipelineDeps) -> HandleResult:
    """Explicit, numbered 11-stage pipeline orchestrator."""
    log = deps.logger.bind(trace_id=msg.trace_id, thread_id=msg.scope.thread_id)
    ctx = CallContext(scope=msg.scope, sender_id=msg.sender_id, trace_id=msg.trace_id)

    # STAGE 1: Injection scan (Record and measure across surfaces, do NOT blindly block)
    inj_scan = scan_injection(msg.text)
    if inj_scan.suspicious:
        log.warning("Detected potential prompt injection/jailbreak", patterns=inj_scan.patterns, types=inj_scan.attack_type)

    # STAGE 2: Mention check & extraction
    mention_re = build_mention_regex(deps.bot_names)
    mention_verdict = extract_mention(msg.text, mention_re)
    cleaned_query = mention_verdict.cleaned_text if isinstance(mention_verdict, MentionFound) else msg.text

    # STAGE 3: Command parsing (Runs BEFORE rate limit so users can always delete their data)
    cmd_outcome = parse_command(cleaned_query)
    if isinstance(cmd_outcome, Answer):
        await send_response(cmd_outcome.text, msg.scope, deps.channel, user_pii=frozenset(), reply_to_id=msg.id)
        return Handled(replied=True)
    elif isinstance(cmd_outcome, AskConfirm):
        await send_response(cmd_outcome.prompt, msg.scope, deps.channel, user_pii=frozenset(), reply_to_id=msg.id)
        return Handled(replied=True)

    # STAGE 4: Rate limit check
    rate_res = await deps.rate_limiter.check(msg.scope, msg.sender_id)
    if isinstance(rate_res, Silent):
        log.info("Rate limit exceeded silently; dropping message")
        return Handled(replied=False)
    elif isinstance(rate_res, Warn):
        await send_response("Bạn đang gửi tin quá nhanh. Vui lòng thử lại sau.", msg.scope, deps.channel, user_pii=frozenset(), reply_to_id=msg.id)
        return Handled(replied=True)

    # STAGE 5: Deferred write execution (After rate limit passed)
    if isinstance(cmd_outcome, DeferredWrite):
        log.info(f"Executing deferred memory write: {cmd_outcome.key}")
        # Append fact to memory
        return Handled(replied=True)

    # STAGE 6: Persist inbound message to history BEFORE model call (If model crashes, query remains safely logged)
    inbound_stored = StoredMessage(
        id=msg.id,
        role="user",
        text=cleaned_query,
        sender_id=msg.sender_id,
        created_at_epoch=time.time(),
    )
    await deps.memory.append(msg.scope, inbound_stored)

    # STAGE 7: Background typing indicator (Does not block main path)
    typing_task = start_typing(deps.channel, msg.scope, log)

    try:
        # STAGE 8: Read memory in PARALLEL
        recent_coro = deps.memory.recent(msg.scope, limit=10)
        summary_coro = deps.memory.summary(msg.scope)
        facts_coro = deps.memory.facts(msg.scope, subject_id=msg.sender_id, query=cleaned_query)

        recent_msgs, summary_text, facts_list = await asyncio.gather(recent_coro, summary_coro, facts_coro)
        facts_rendered = "\n".join(f"- {f.text}" for f in facts_list) if facts_list else None

        # STAGE 9: Assemble context envelope
        envelope = assemble_context_envelope(
            question=cleaned_query,
            recent_history=recent_msgs,
            user_facts=facts_rendered,
            summary=summary_text,
        )

        # STAGE 10: Generate via ReAct loop
        gen_result = await generate_react_loop(
            envelope=envelope,
            llm=deps.llm,
            tools=deps.tools,
            rate_limiter=deps.rate_limiter,
            ctx=ctx,
            should_stop_hook=deps.should_stop_hook,
            default_model=deps.default_model,
        )

        # So khớp tagged union bằng `isinstance`, đúng quy ước của dự án: nó thu
        # hẹp kiểu ở CẢ HAI nhánh, còn TypeGuard (`is_ok`/`is_err`) chỉ thu hẹp ở
        # nhánh đúng nên dòng lấy `.value` phía sau vẫn không được kiểm kiểu.
        if isinstance(gen_result, Err):
            err = gen_result.error
            log.error("Generation failed", error=err)
            # Hai quyết định tách bạch, cố ý không gộp: (1) còn đáng thử lại không,
            # (2) lỗi này có được phép trả lời ra ngoài không.
            if not is_retryable(err) or deps.is_final_attempt:  # noqa: SIM102
                if not is_silent(err):
                    await send_response("Xin lỗi, hệ thống tạm thời không thể xử lý yêu cầu.", msg.scope, deps.channel, user_pii=frozenset(), reply_to_id=msg.id)
                    return Failed(error=err, replied=True)
            return Failed(error=err, replied=False)

        generated_text = gen_result.value

        # STAGE 11: Respond with output rails
        user_pii = frozenset([word for word in cleaned_query.split() if "@" in word or word.isdigit()])
        await send_response(
            raw_text=generated_text,
            scope=msg.scope,
            channel=deps.channel,
            user_pii=user_pii,
            has_retrieved_knowledge=envelope.has_knowledge,
            reply_to_id=msg.id,
        )

        # Record bot response in memory
        bot_stored = StoredMessage(
            id=f"{msg.id}:bot",
            role="assistant",
            text=generated_text,
            sender_id="bot",
            created_at_epoch=time.time(),
        )
        await deps.memory.append(msg.scope, bot_stored)

        return Handled(replied=True)

    finally:
        if not typing_task.done():
            typing_task.cancel()
