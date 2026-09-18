import time
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from typing import Any

from contracts.trace import SpanEvent, TraceContext

_current_trace_context: ContextVar[TraceContext | None] = ContextVar("_current_trace_context", default=None)


def get_current_trace_id() -> str:
    ctx = _current_trace_context.get()
    return ctx.trace_id if ctx else f"trc-{uuid.uuid4().hex[:12]}"


def get_current_trace_context() -> TraceContext | None:
    return _current_trace_context.get()


def set_trace_context(ctx: TraceContext) -> None:
    _current_trace_context.set(ctx)


class Tracer:
    """Manages distributed tracing spans for AI requests."""

    @staticmethod
    def start_trace(request_id: str, tenant_id: str = "default", user_id: str = "anonymous") -> TraceContext:
        trace_id = f"trc-{uuid.uuid4().hex[:16]}"
        span_id = f"spn-{uuid.uuid4().hex[:8]}"
        ctx = TraceContext(
            trace_id=trace_id,
            span_id=span_id,
            request_id=request_id,
            tenant_id=tenant_id,
            user_id=user_id,
            spans=[],
        )
        set_trace_context(ctx)
        return ctx

    @staticmethod
    def add_span(name: str, duration_ms: float, attributes: dict[str, Any] | None = None) -> None:
        ctx = _current_trace_context.get()
        if ctx:
            span = SpanEvent(
                name=name,
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                attributes=attributes or {},
            )
            ctx.spans.append(span)


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Generator[dict[str, Any], None, None]:
    """Context manager to measure and record duration of a sub-step (RAG, Guardrail, LLM call)."""
    start_time = time.perf_counter()
    attrs = dict(attributes or {})
    try:
        yield attrs
    finally:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        Tracer.add_span(name=name, duration_ms=round(elapsed_ms, 2), attributes=attrs)
