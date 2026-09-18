import re
from typing import NamedTuple


class TopicScanResult(NamedTuple):
    is_forbidden: bool
    category: str


_FORBIDDEN_PATTERNS = [
    (re.compile(r"\b(tự tử|chế tạo bom|vũ khí sinh học|malware code)\b", re.IGNORECASE), "extremism_or_weapons"),
    (re.compile(r"\b(tấn công ddos|exploit sql injection|hack ngân hàng)\b", re.IGNORECASE), "cyberattack"),
]


def check_forbidden_topics(text: str) -> TopicScanResult:
    for pattern, category in _FORBIDDEN_PATTERNS:
        if pattern.search(text):
            return TopicScanResult(is_forbidden=True, category=category)
    return TopicScanResult(is_forbidden=False, category="")
