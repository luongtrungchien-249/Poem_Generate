import re
from typing import NamedTuple


class ToxicityScanResult(NamedTuple):
    is_toxic: bool
    score: float
    categories: list[str]


_TOXIC_PATTERNS = [
    (re.compile(r"\b(chết tiệt|đồ ngu|thằng khốn|mất dạy)\b", re.IGNORECASE), "profanity_vi"),
    (re.compile(r"\b(hate speech|kill yourself|idiot|scam)\b", re.IGNORECASE), "harassment_en"),
]


def check_toxicity(text: str) -> ToxicityScanResult:
    matched = []
    for pat, cat in _TOXIC_PATTERNS:
        if pat.search(text):
            matched.append(cat)

    is_toxic = len(matched) > 0
    score = 0.85 if is_toxic else 0.0
    return ToxicityScanResult(is_toxic=is_toxic, score=score, categories=matched)
