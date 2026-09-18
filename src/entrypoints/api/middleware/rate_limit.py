import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from contracts.error import ErrorCode, ErrorResponse


class TokenBucket:
    def __init__(self, capacity: int = 60, refill_rate: float = 1.0) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()

    def consume(self, amount: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(float(self.capacity), self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token bucket rate limiter per tenant."""

    def __init__(self, app, capacity: int = 60, refill_rate: float = 2.0) -> None:
        super().__init__(app)
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: dict[str, TokenBucket] = {}

    def _get_bucket(self, tenant_id: str) -> TokenBucket:
        if tenant_id not in self.buckets:
            self.buckets[tenant_id] = TokenBucket(self.capacity, self.refill_rate)
        return self.buckets[tenant_id]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        # Exclude health endpoints from rate limiting
        if request.url.path in ["/healthz", "/readyz", "/metrics"]:
            return await call_next(request)

        tenant_id = request.headers.get("X-Tenant-ID") or "default"
        bucket = self._get_bucket(tenant_id)

        if not bucket.consume(1):
            trace_id = getattr(request.state, "trace_id", None)
            err = ErrorResponse(
                error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
                message=f"Rate limit exceeded for tenant '{tenant_id}'. Please retry later.",
                trace_id=trace_id,
            )
            return JSONResponse(status_code=429, content=err.model_dump())

        return await call_next(request)
