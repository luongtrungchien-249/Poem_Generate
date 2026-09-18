import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from adapters.observability.tracing import Tracer


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Extracts or initializes tracing context, request ID, tenant ID, and sets response headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:12]}"
        tenant_id = request.headers.get("X-Tenant-ID") or "default"
        user_id = request.headers.get("X-User-ID") or "anonymous"

        trace_ctx = Tracer.start_trace(request_id=request_id, tenant_id=tenant_id, user_id=user_id)
        # Store in request state for convenient dependency access
        request.state.trace_id = trace_ctx.trace_id
        request.state.request_id = request_id
        request.state.tenant_id = tenant_id
        request.state.user_id = user_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Trace-ID"] = trace_ctx.trace_id
        return response
