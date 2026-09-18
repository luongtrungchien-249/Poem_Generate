"""Kiểu dùng chung của domain: Result và cây lỗi nghiệp vụ."""

from .errors import (
    BadPayload,
    BotError,
    BudgetExceeded,
    NotAllowed,
    RateLimited,
    UpstreamError,
    UpstreamTimeout,
    is_config_error,
    is_retryable,
    is_silent,
)
from .result import Err, Ok, Result, is_err, is_ok

__all__ = [
    "Ok", "Err", "Result", "is_ok", "is_err",
    "BotError", "RateLimited", "BudgetExceeded", "NotAllowed",
    "UpstreamTimeout", "UpstreamError", "BadPayload",
    "is_config_error", "is_retryable", "is_silent",
]
