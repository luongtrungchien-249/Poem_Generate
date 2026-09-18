import re
from typing import NamedTuple


class InjectionScanResult(NamedTuple):
    is_injection: bool
    matched_patterns: list[str]
    confidence: float


# Compiled injection & jailbreak regex patterns (Vietnamese & English)
_INJECTION_PATTERNS = [
    (re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts|rules)", re.IGNORECASE), "ignore_previous_instructions"),
    (re.compile(r"bỏ\s+qua\s+(toàn\s+bộ\s+)?(hướng\s+dẫn|chỉ\s+thị|quy\s+tắc)\s+(trước|ban\s+đầu)", re.IGNORECASE), "ignore_instructions_vi"),
    (re.compile(r"system\s+prompt\s+(override|reveal|leak|print)", re.IGNORECASE), "system_prompt_override"),
    (re.compile(r"(tiết\s+lộ|in\s+ra|hiển\s+thị)\s+(system\s+prompt|lệnh\s+hệ\s+thống)", re.IGNORECASE), "system_prompt_reveal_vi"),
    (re.compile(r"\b(DAN|jailbreak|do\s+anything\s+now)\b", re.IGNORECASE), "jailbreak_keyword"),
    (re.compile(r"(bạn\s+không\s+còn\s+bị\s+ràng\s+buộc|quên\s+hết\s+quy\s+định)", re.IGNORECASE), "unrestricted_roleplay_vi"),
]


def detect_injection(text: str) -> InjectionScanResult:
    matched = []
    for pattern, name in _INJECTION_PATTERNS:
        if pattern.search(text):
            matched.append(name)

    is_injection = len(matched) > 0
    confidence = min(1.0, 0.5 + (len(matched) * 0.3)) if is_injection else 0.0
    return InjectionScanResult(
        is_injection=is_injection,
        matched_patterns=matched,
        confidence=round(confidence, 2),
    )
