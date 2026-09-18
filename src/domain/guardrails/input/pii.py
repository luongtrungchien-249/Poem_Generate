import re
from typing import NamedTuple


class PIIScanResult(NamedTuple):
    has_pii: bool
    masked_text: str
    detected_types: list[str]


# Common PII Regexes
_EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
_PHONE_VN_REGEX = re.compile(r"\b(0[3|5|7|8|9][0-9]{8}|\+84[3|5|7|8|9][0-9]{8})\b")
_CREDIT_CARD_REGEX = re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")
_ID_CARD_VN_REGEX = re.compile(r"\b\d{12}\b") # CCCD Việt Nam (12 chữ số)


def mask_pii(text: str) -> PIIScanResult:
    detected = []
    masked = text

    if _EMAIL_REGEX.search(masked):
        detected.append("email")
        masked = _EMAIL_REGEX.sub("[REDACTED_EMAIL]", masked)

    if _PHONE_VN_REGEX.search(masked):
        detected.append("phone_vn")
        masked = _PHONE_VN_REGEX.sub("[REDACTED_PHONE]", masked)

    if _CREDIT_CARD_REGEX.search(masked):
        detected.append("credit_card")
        masked = _CREDIT_CARD_REGEX.sub("[REDACTED_CARD]", masked)

    if _ID_CARD_VN_REGEX.search(masked):
        detected.append("id_card_vn")
        masked = _ID_CARD_VN_REGEX.sub("[REDACTED_ID]", masked)

    return PIIScanResult(
        has_pii=len(detected) > 0,
        masked_text=masked,
        detected_types=detected,
    )
