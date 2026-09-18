import re
from dataclasses import dataclass
from typing import TypeAlias


@dataclass(frozen=True, slots=True)
class Answer:
    text: str


@dataclass(frozen=True, slots=True)
class AskConfirm:
    prompt: str
    fact_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DeferredWrite:
    """Postpones expensive memory write until after rate limit & budget checks pass."""
    key: str
    value: str


@dataclass(frozen=True, slots=True)
class NoCommand:
    pass


CommandOutcome: TypeAlias = Answer | AskConfirm | DeferredWrite | NoCommand

_EXACT_COMMANDS: dict[str, str] = {
    "/help": "Hệ thống AI Platform hỗ trợ: tra cứu tài liệu (/kb), ghi nhớ (/remember [thông tin]), xoá dữ liệu (/forget).",
    "/ping": "pong",
    "/status": "Hệ thống hoạt động bình thường, tất cả các cổng đều sẵn sàng.",
}

_REMEMBER_REGEX = re.compile(r"^/(?:remember|ghinho)\s+([a-zA-Z0-9_\-]+)\s*[:=]\s*(.+)$", re.IGNORECASE)
_FORGET_REGEX = re.compile(r"^/(?:forget|xoa)\s*(.*)$", re.IGNORECASE)
_CONFIRM_REGEX = re.compile(r"^/(?:confirm|dongy)\s*([0-9,\s]*)$", re.IGNORECASE)


def parse_command(cleaned_text: str) -> CommandOutcome:
    trimmed = cleaned_text.strip()
    lowered = trimmed.lower()

    # 1. Exact lookup
    if lowered in _EXACT_COMMANDS:
        return Answer(text=_EXACT_COMMANDS[lowered])

    # 2. Remember command -> returns DeferredWrite
    rem_match = _REMEMBER_REGEX.match(trimmed)
    if rem_match:
        key, val = rem_match.group(1), rem_match.group(2)
        return DeferredWrite(key=key, value=val)

    # 3. Forget command
    forget_match = _FORGET_REGEX.match(trimmed)
    if forget_match:
        pattern = forget_match.group(1).strip()
        return AskConfirm(prompt=f"Bạn có chắc chắn muốn xoá dữ liệu khớp với '{pattern}'?", fact_ids=())

    return NoCommand()
