from dataclasses import dataclass
from typing import TypeAlias


@dataclass(frozen=True, slots=True)
class RateLimited:
    tier: str
    retry_after_ms: int
    silent: bool = False


@dataclass(frozen=True, slots=True)
class BudgetExceeded:
    scope_name: str
    limit: int
    current: int


@dataclass(frozen=True, slots=True)
class NotAllowed:
    reason: str
    policy: str
    silent: bool = True


@dataclass(frozen=True, slots=True)
class UpstreamTimeout:
    upstream: str
    timeout_sec: float


@dataclass(frozen=True, slots=True)
class UpstreamError:
    upstream: str
    status_code: int | None = None
    message: str = ""


@dataclass(frozen=True, slots=True)
class BadPayload:
    reason: str


@dataclass(frozen=True, slots=True)
class OutputKhongDat:
    """Đầu ra không thoả ràng buộc cứng của thể loại, sau khi đã hết lượt sửa.

    Mang theo chẩn đoán để tầng trên giải thích được cho người dùng vì sao không
    có kết quả, thay vì trả ra một bài sai luật. `chan_doan` là văn bản đã được
    dựng sẵn ở tầng application — domain không biết thơ là gì.
    """

    ma_the: str
    so_luot_da_sua: int
    chan_doan: str


BotError: TypeAlias = (
    RateLimited
    | BudgetExceeded
    | NotAllowed
    | UpstreamTimeout
    | UpstreamError
    | BadPayload
    | OutputKhongDat
)


def is_config_error(e: BotError) -> bool:
    """Returns True if error is due to bad credentials/config (401/403) where retrying is futile."""
    return bool(isinstance(e, UpstreamError) and e.status_code in (401, 403))


def is_retryable(e: BotError) -> bool:
    """Returns True if error is transient (network timeout, 429, 5xx, or status_code is None).

    OutputKhongDat KHÔNG đáng thử lại: vòng sửa ở tầng trên đã thử hết lượt rồi,
    chạy lại job chỉ tốn thêm tiền mà không đổi kết cục.
    """
    if isinstance(e, UpstreamTimeout):
        return True
    if isinstance(e, UpstreamError):
        # By architectural rule: status is None implies network drop -> benefit of the doubt: retry
        if e.status_code is None:
            return True
        return e.status_code == 429 or e.status_code >= 500
    return bool(isinstance(e, RateLimited))


def is_silent(e: BotError) -> bool:
    """Returns True if the bot should fail silently without sending noisy error messages to group chat."""
    if isinstance(e, RateLimited) and e.silent:
        return True
    return bool(isinstance(e, NotAllowed) and e.silent)
