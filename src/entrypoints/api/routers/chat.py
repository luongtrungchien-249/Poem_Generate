import json
import time
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from adapters.observability.metrics import metrics
from adapters.observability.tracing import get_current_trace_id, trace_span
from contracts.chat import ChatRequest, ChatResponse, Message, Role
from domain.guardrails.input import (
    check_forbidden_topics,
    check_input_length,
    detect_injection,
    mask_pii,
)
from domain.guardrails.output import enforce_output_guardrails
from domain.guardrails.output.streaming import Chan, StreamingOutputGuard
from entrypoints.api.deps import AppContainer, get_container
from entrypoints.api.middleware.auth import tenant_scope_cua

router = APIRouter(prefix="/v1", tags=["Chat"])


@router.post("/chat", response_model=None)
async def chat_endpoint(
    req: ChatRequest,
    raw_request: Request,
    app_container: AppContainer = Depends(get_container),
):
    start_time = time.perf_counter()
    trace_id = getattr(raw_request.state, "trace_id", get_current_trace_id())
    # G10 — tenant đến từ XÁC THỰC, KHÔNG từ thân request.
    #
    # Bản trước: `req.tenant_id or ...` — người gọi tự khai tenant của mình. Mọi
    # cô lập ở tầng dưới đều vô nghĩa khi danh tính do chính người gọi đặt.
    # `req.tenant_id` nay bị BỎ QUA hoàn toàn; có test ghim điều đó.
    scope = tenant_scope_cua(raw_request)
    tenant_id: str = scope.tenant_id
    # Danh tính người gọi hiện chưa được dùng: Bước 3 sẽ đưa nó vào RequestContext
    # để bộ nhớ hồ sơ và kiểm soát truy cập theo người dùng hoạt động.
    _user_id = req.user_id or getattr(raw_request.state, "user_id", "anonymous")

    # 1. Extract latest user query
    user_msgs = [m for m in req.messages if m.role == Role.USER]
    if not user_msgs:
        raise HTTPException(status_code=400, detail="At least one user message is required.")
    last_user_msg = user_msgs[-1]
    raw_query = last_user_msg.content

    # 2. Input Guardrails
    if req.enable_guardrails:
        len_res = check_input_length(raw_query)
        if not len_res.is_valid:
            raise HTTPException(status_code=400, detail=len_res.reason)

        inj_res = detect_injection(raw_query)
        if inj_res.is_injection:
            raise HTTPException(
                status_code=400,
                detail=f"Security Guardrail Triggered: Potential prompt injection detected ({', '.join(inj_res.matched_patterns)}).",
            )

        # §17.3 — phân loại chủ đề. TRƯỚC 21/09/2026 `check_forbidden_topics` tồn
        # tại nhưng không đường nào gọi tới: một rào chắn không được nối thì chỉ
        # làm cho bản kiểm kê trông đầy đủ.
        topic_res = check_forbidden_topics(raw_query)
        if topic_res.muc == "BLOCK":
            raise HTTPException(
                status_code=400,
                detail=f"Chủ đề không được hỗ trợ ({topic_res.category}): {topic_res.ly_do}",
            )
        # REVIEW thì VẪN xử lý — đánh dấu để HITL (§22) xem lại, không chặn người
        # dùng chỉ vì họ nói nặng lời. Chặn ở đây là biến bộ lọc thành bộ kiểm duyệt.
        can_xem_lai = topic_res.muc == "REVIEW"

        # Mask PII
        pii_res = mask_pii(raw_query)
        last_user_msg.content = pii_res.masked_text

    else:
        can_xem_lai = False

    # 3. Model selection & routing
    chosen_model = app_container.router.select_model(
        explicit_model=req.model,
        tier=req.tier,
        query_text=raw_query,
    )
    fallback_chain = app_container.router.get_fallback_chain(chosen_model)

    # 4. RAG context retrieval
    citations: list[dict[str, Any]] = []
    rag_context = ""
    valid_chunk_ids = []
    if req.enable_rag:
        with trace_span("rag_retrieval", {"query": raw_query}):
            retrieved = await app_container.retriever.retrieve(
                scope,
                query=raw_query,
                top_k=4,
                # 🩸 `filters={"tenant_id": ...}` ĐÃ BỎ: tenant lọc trên field qua
                # `scope`, không qua metadata. Xem docstring của InMemoryVectorRepository.
            )
            reranked = await app_container.reranker.rerank(raw_query, retrieved, top_n=3)
            rag_context, citations = app_container.context_assembler.assemble(reranked)
            valid_chunk_ids = [c["chunk_id"] for c in citations]

    # 5. Session Memory
    session_messages = list(req.messages)
    if req.session_id:
        with trace_span("load_session_memory"):
            history = await app_container.session_memory.get_recent_messages(
                scope, req.session_id
            )
            if history:
                session_messages = history + [last_user_msg]

    # If RAG is enabled, inject system prompt with context
    if req.enable_rag and rag_context:
        template = app_container.prompt_reg.get("rag_answer", version="v1")
        rendered_sys, _ = template.render(context=rag_context, question=last_user_msg.content)
        # Prepend or update system message
        session_messages = [Message(role=Role.SYSTEM, content=rendered_sys)] + [
            m for m in session_messages if m.role != Role.SYSTEM
        ]

    # 6. Streaming or Non-streaming execution
    if req.stream:
        async def event_generator() -> AsyncIterator[str]:
            metrics.active_requests.inc()
            first_token_recorded = False
            token_start = time.perf_counter()

            # 🔴 LỖ HỔNG ĐÃ VÁ 21/09/2026. Bản trước yield thẳng `chunk.delta` ra
            # SSE, nên `stream=true` đi vòng qua TOÀN BỘ output rails — bật stream
            # là tắt rào chắn đầu ra. Nay mọi mẩu đều phải qua guard.
            #
            # Guard giữ lại một cửa sổ ký tự cuối trước khi phát, để một mẫu bị cắt
            # đôi giữa hai chunk vẫn bị bắt TRƯỚC khi nửa đầu kịp đi ra. Đánh đổi:
            # chữ hiện chậm hơn vài chục ký tự. Xem docstring của module guard.
            guard = (
                StreamingOutputGuard(valid_chunk_ids=list(valid_chunk_ids))
                if req.enable_guardrails
                else None
            )

            def _su_kien(**truong: Any) -> str:
                return f"data: {json.dumps(truong, ensure_ascii=False)}\n\n"

            try:
                async for chunk in app_container.streamer.stream(
                    messages=session_messages,
                    model=chosen_model,
                    temperature=req.temperature,
                    max_tokens=req.max_tokens,
                ):
                    if not first_token_recorded and chunk.delta:
                        ttft = time.perf_counter() - token_start
                        metrics.time_to_first_token.labels(model=chosen_model).observe(ttft)
                        first_token_recorded = True

                    if guard is None:
                        phat = chunk.delta
                    else:
                        kq = guard.nap(chunk.delta)
                        if isinstance(kq, Chan):
                            # FAIL CLOSED giữa luồng: không phát thêm chữ nào nữa.
                            yield _su_kien(
                                delta="", finish_reason="blocked_by_guardrail",
                                error=kq.ly_do, trace_id=trace_id,
                            )
                            metrics.record_request(
                                "/v1/chat", tenant_id, "400",
                                time.perf_counter() - start_time, chosen_model,
                            )
                            return
                        phat = kq.text

                    # Mẩu rỗng vì đang bị giữ lại thì KHÔNG phát sự kiện trống —
                    # trừ mẩu mang `finish_reason`, vốn là tín hiệu chứ không phải chữ.
                    if phat or chunk.finish_reason:
                        yield _su_kien(
                            delta=phat,
                            finish_reason=chunk.finish_reason,
                            trace_id=trace_id,
                            citation_ids=valid_chunk_ids if chunk.finish_reason else None,
                        )

                # Xả nốt phần còn giữ lại, sau khi soi lần cuối trên toàn văn.
                if guard is not None:
                    cuoi = guard.ket_thuc()
                    if isinstance(cuoi, Chan):
                        yield _su_kien(
                            delta="", finish_reason="blocked_by_guardrail",
                            error=cuoi.ly_do, trace_id=trace_id,
                        )
                        metrics.record_request(
                            "/v1/chat", tenant_id, "400",
                            time.perf_counter() - start_time, chosen_model,
                        )
                        return
                    if cuoi.text:
                        yield _su_kien(delta=cuoi.text, finish_reason=None, trace_id=trace_id)

                yield "data: [DONE]\n\n"

                # Lưu vào bộ nhớ phiên VĂN BẢN ĐÃ QUA RÀO, không phải văn bản thô.
                # Lưu bản thô thì PII đã bị che ở đầu ra lại nằm nguyên trong lịch
                # sử, và sẽ quay lại prompt ở lượt sau — rò qua đường vòng.
                if req.session_id:
                    da_sinh = guard.toan_van if guard is not None else ""
                    await app_container.session_memory.add_message(scope, req.session_id, last_user_msg)
                    await app_container.session_memory.add_message(
                        scope, req.session_id, Message(role=Role.ASSISTANT, content=da_sinh)
                    )

                duration = time.perf_counter() - start_time
                metrics.record_request("/v1/chat", tenant_id, "200", duration, chosen_model)

            finally:
                metrics.active_requests.dec()

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    # Non-streaming response
    with trace_span("llm_generate", {"model": chosen_model}):
        async def call_llm(model_name: str):
            return await app_container.generator.generate(
                messages=session_messages,
                model=model_name,
                temperature=req.temperature,
                max_tokens=req.max_tokens,
            )

        llm_resp = await app_container.fallback_mgr.execute_with_fallback(
            primary_model=chosen_model,
            fallback_models=fallback_chain,
            func=call_llm,
        )

    # 7. Output Guardrails
    verdict = None
    final_content = llm_resp.content
    if req.enable_guardrails:
        verdict = enforce_output_guardrails(final_content, valid_chunk_ids=valid_chunk_ids)
        if not verdict.allowed:
            raise HTTPException(status_code=400, detail=verdict.rejection_reason)
        final_content = verdict.sanitized_text

    # 8. Record session memory
    if req.session_id:
        await app_container.session_memory.add_message(scope, req.session_id, last_user_msg)
        await app_container.session_memory.add_message(
            scope, req.session_id, Message(role=Role.ASSISTANT, content=final_content)
        )

    # 9. Observability & Metrics
    duration = time.perf_counter() - start_time
    metrics.record_request("/v1/chat", tenant_id, "200", duration, chosen_model)
    prompt_toks = llm_resp.usage.get("prompt_tokens", 0)
    compl_toks = llm_resp.usage.get("completion_tokens", 0)
    metrics.record_tokens(chosen_model, prompt_toks, compl_toks)

    return ChatResponse(
        content=final_content,
        model=llm_resp.model,
        finish_reason=llm_resp.finish_reason,
        usage=llm_resp.usage,
        cost_usd=llm_resp.cost_usd,
        trace_id=trace_id,
        citations=citations,
        guardrail_verdict=(
            {"allowed": True, "can_xem_lai": can_xem_lai} if verdict else None
        ),
    )
