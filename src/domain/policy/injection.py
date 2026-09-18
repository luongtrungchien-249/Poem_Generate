import re
import unicodedata
from dataclasses import dataclass
from typing import Literal

Loai = Literal["injection", "jailbreak"]


def fold_diacritics(text: str) -> str:
    """Decomposes Unicode (NFD), strips combining accents, and replaces 'đ'/'Đ' manually."""
    # NFD decomposition
    nfd = unicodedata.normalize("NFD", text)
    # Remove combining marks
    without_marks = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    # Manual 'đ'/'Đ' replacement
    return without_marks.replace("đ", "d").replace("Đ", "D")


_MAU: list[tuple[str, Loai, re.Pattern[str]]] = [
    ("ignore_instructions", "injection", re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE)),
    ("bo_qua_chi_thi", "injection", re.compile(r"bo\s+qua\s+(toan\s+bo\s+)?(huong\s+dan|chi\s+thi|quy\s+tac)", re.IGNORECASE)),
    ("reveal_system_prompt", "injection", re.compile(r"(reveal|print|show|tiet\s+lo|hien\s+thi)\s+system\s+prompt", re.IGNORECASE)),
    ("jailbreak_dan", "jailbreak", re.compile(r"\b(dan|jailbreak|do\s+anything\s+now)\b", re.IGNORECASE)),
    ("unrestricted_mode", "jailbreak", re.compile(r"khong\s+con\s+bi\s+rang\s+buoc|quen\s+het\s+quy\s+dinh", re.IGNORECASE)),
]


@dataclass(frozen=True, slots=True)
class InjectionScan:
    suspicious: bool
    patterns: tuple[str, ...]
    attack_type: tuple[Loai, ...]


def scan_injection(text: str) -> InjectionScan:
    """Scans text against attack patterns on folded diacritics. Designed to measure and record across all surfaces."""
    folded = fold_diacritics(text)
    matched_patterns = []
    matched_types: set[Loai] = set()

    for name, loai, pattern in _MAU:
        if pattern.search(folded):
            matched_patterns.append(name)
            matched_types.add(loai)

    return InjectionScan(
        suspicious=len(matched_patterns) > 0,
        patterns=tuple(matched_patterns),
        attack_type=tuple(matched_types),
    )
