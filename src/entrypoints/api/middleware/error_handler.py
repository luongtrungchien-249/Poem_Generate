import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from adapters.llm.resilience import CircuitBreakerOpenException
from contracts.error import ErrorCode, ErrorResponse

logger = logging.getLogger("error_handler")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Translates unhandled exceptions into structured ErrorResponse contracts."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try:
            return await call_next(request)
        except CircuitBreakerOpenException as cbe:
            trace_id = getattr(request.state, "trace_id", None)
            err = ErrorResponse(
                error_code=ErrorCode.CIRCUIT_OPEN,
                message=f"Circuit breaker is OPEN: {str(cbe)}",
                trace_id=trace_id,
            )
            return JSONResponse(status_code=503, content=err.model_dump())
        except ValueError as ve:
            trace_id = getattr(request.state, "trace_id", None)
            err = ErrorResponse(
                error_code=ErrorCode.INVALID_REQUEST,
                message=str(ve),
                trace_id=trace_id,
            )
            return JSONResponse(status_code=400, content=err.model_dump())
        except Exception as exc:
            logger.exception("Unhandled server exception occurred")
            trace_id = getattr(request.state, "trace_id", None)
            err = ErrorResponse(
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                message="An internal server error occurred. Please contact support with trace_id.",
                trace_id=trace_id,
                details={"exception_type": exc.__class__.__name__},
            )
            return JSONResponse(status_code=500, content=err.model_dump())
