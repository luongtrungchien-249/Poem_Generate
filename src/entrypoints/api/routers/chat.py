import json
import time
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from adapters.observability.metrics import metrics
from adapters.observability.tracing import get_current_trace_id, trace_span
from contracts.chat import ChatRequest, ChatResponse, Message, Role
from domain.guardrails.input import check_input_length, detect_injection, mask_pii
from domain.guardrails.output import enforce_output_guardrails
from entrypoints.api.deps import AppContainer, get_container

router = APIRouter(prefix="/v1", tags=["Chat"])


@router.post("/chat", response_model=None)
async def chat_endpoint(
    req: ChatRequest,
    raw_request: Request,
    app_container: AppContainer = Depends(get_container),
):
    start_time = time.perf_counter()
    trace_id = getattr(raw_request.state, "trace_id", get_current_trace_id())
    tenant_id: str = req.tenant_id or str(getattr(raw_request.state, "tenant_id", "default"))
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

        # Mask PII
        pii_res = mask_pii(raw_query)
        last_user_msg.content = pii_res.masked_text

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
                query=raw_query,
                top_k=4,
                filters={"tenant_id": tenant_id},
            )
            reranked = await app_container.reranker.rerank(raw_query, retrieved, top_n=3)
            rag_context, citations = app_container.context_assembler.assemble(reranked)
            valid_chunk_ids = [c["chunk_id"] for c in citations]

    # 5. Session Memory
    session_messages = list(req.messages)
    if req.session_id:
        with trace_span("load_session_memory"):
            history = await app_container.session_memory.get_recent_messages(req.session_id)
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
            full_content = []

            try:
                async for chunk in app_container.default_llm.stream(
                    messages=session_messages,
                    model=chosen_model,
                    temperature=req.temperature,
                    max_tokens=req.max_tokens,
                ):
                    if not first_token_recorded and chunk.delta:
                        ttft = time.perf_counter() - token_start
                        metrics.time_to_first_token.labels(model=chosen_model).observe(ttft)
                        first_token_recorded = True

                    full_content.append(chunk.delta)
                    data = {
                        "delta": chunk.delta,
                        "finish_reason": chunk.finish_reason,
                        "trace_id": trace_id,
                        "citation_ids": valid_chunk_ids if chunk.finish_reason else None,
                    }
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

                yield "data: [DONE]\n\n"

                # Save turn to session memory if provided
                if req.session_id:
                    await app_container.session_memory.add_message(req.session_id, last_user_msg)
                    await app_container.session_memory.add_message(
                        req.session_id, Message(role=Role.ASSISTANT, content="".join(full_content))
                    )

                duration = time.perf_counter() - start_time
                metrics.record_request("/v1/chat", tenant_id, "200", duration, chosen_model)

            finally:
                metrics.active_requests.dec()

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    # Non-streaming response
    with trace_span("llm_generate", {"model": chosen_model}):
        async def call_llm(model_name: str):
            return await app_container.default_llm.generate(
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
        await app_container.session_memory.add_message(req.session_id, last_user_msg)
        await app_container.session_memory.add_message(
            req.session_id, Message(role=Role.ASSISTANT, content=final_content)
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
        guardrail_verdict={"allowed": True} if verdict else None,
    )
