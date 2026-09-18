import re
from dataclasses import dataclass
from typing import TypeAlias

_VOWEL_MAP = {
    "a": "[aàáảãạăằắẳẵặâầấẩẫậ]",
    "e": "[eèéẻẽẹêềếểễệ]",
    "i": "[iìíỉĩị]",
    "o": "[oòóỏõọôồốổỗộơờớởỡợ]",
    "u": "[uùúủũụưừứửữự]",
    "y": "[yỳýỷỹỵ]",
}


def build_mention_regex(bot_names: tuple[str, ...]) -> re.Pattern[str]:
    """Generates a dynamic regex matching bot mentions with Vietnamese accent expansion and negative lookaheads."""
    # 1. Sort longest first so shorter prefixes don't prematurely swallow longer names
    sorted_names = sorted(bot_names, key=len, reverse=True)

    patterns = []
    for name in sorted_names:
        lowered = name.lower()
        expanded = []
        for ch in lowered:
            if ch in _VOWEL_MAP:
                expanded.append(_VOWEL_MAP[ch])
            elif ch == "_":
                expanded.append(r"[_\s]?")
            else:
                expanded.append(re.escape(ch))
        # Trailing boundary: cannot be immediately followed by another letter, digit, or underscore
        patterns.append("".join(expanded) + r"(?![^\W\d_]|\d|_)")

    combined = r"(?:@|\b)(" + "|".join(patterns) + r")\b"
    return re.compile(combined, re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class MentionFound:
    matched_name: str
    cleaned_text: str


@dataclass(frozen=True, slots=True)
class NoMention:
    pass


MentionVerdict: TypeAlias = MentionFound | NoMention


def extract_mention(text: str, regex: re.Pattern[str]) -> MentionVerdict:
    match = regex.search(text)
    if not match:
        return NoMention()
    # Strip mention cleanly from user text
    cleaned = regex.sub("", text).strip()
    return MentionFound(matched_name=match.group(0), cleaned_text=cleaned)
