from typing import NamedTuple


class LengthCheckResult(NamedTuple):
    is_valid: bool
    reason: str


def check_input_length(text: str, min_chars: int = 1, max_chars: int = 10000) -> LengthCheckResult:
    length = len(text.strip())
    if length < min_chars:
        return LengthCheckResult(is_valid=False, reason=f"Query is too short (min {min_chars} chars)")
    if length > max_chars:
        return LengthCheckResult(is_valid=False, reason=f"Query exceeds max length of {max_chars} chars")
    return LengthCheckResult(is_valid=True, reason="")
