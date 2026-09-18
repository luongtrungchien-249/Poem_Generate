import re
from dataclasses import dataclass

# Regex for stripping markdown symbols in rule 1
_MD_SYMBOLS = re.compile(r"[*_~`#>]")

# Rule 2: Secret tokens
_SECRETS_REGEX = [
    (re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE), "openai_key"),
    (re.compile(r"ghp_[a-zA-Z0-9]{20,}", re.IGNORECASE), "github_pat"),
    (re.compile(r"postgres://[^\s]+", re.IGNORECASE), "database_url"),
]

# Rule 3: PII
_EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
_PHONE_REGEX = re.compile(r"\b(0[3|5|7|8|9][0-9]{8}|\+84[3|5|7|8|9][0-9]{8})\b")
_CCCD_REGEX = re.compile(r"\b\d{12}\b")


@dataclass(frozen=True, slots=True)
class OutputVerdict:
    """Carries transformation trace rather than just plain text.
    Logs record types only, never raw secret strings, to prevent log leakage.
    """
    text: str
    da_can_thiep: tuple[str, ...]
    loai_bi_mat: tuple[str, ...]
    loai_ca_nhan: tuple[str, ...]
    thieu_trich_dan: bool


def apply_output_guardrails(
    raw_text: str,
    user_provided_pii: frozenset[str],
    has_retrieved_knowledge: bool = False,
    strip_markdown: bool = False,
) -> OutputVerdict:
    """Enforces 4 strictly ordered output guardrail rules."""
    current_text = raw_text
    interventions = []
    secrets_found = []
    pii_found = []

    # Rule 1: FORMAT - Optional markdown stripping
    if strip_markdown:
        current_text = _MD_SYMBOLS.sub("", current_text)
        interventions.append("format_strip_markdown")

    # Rule 2: SECRETS - Unconditional hard masking
    for pattern, secret_type in _SECRETS_REGEX:
        if pattern.search(current_text):
            current_text = pattern.sub("[REDACTED_SECRET]", current_text)
            secrets_found.append(secret_type)
            interventions.append("mask_secret")

    # Rule 3: PERSONAL - Conditional masking: Only mask PII NOT provided by user in this turn
    for match in _EMAIL_REGEX.finditer(current_text):
        email = match.group(0)
        if email not in user_provided_pii:
            current_text = current_text.replace(email, "[REDACTED_EMAIL]")
            pii_found.append("email")
            interventions.append("mask_pii_email")

    for match in _PHONE_REGEX.finditer(current_text):
        phone = match.group(0)
        if phone not in user_provided_pii:
            current_text = current_text.replace(phone, "[REDACTED_PHONE]")
            pii_found.append("phone")
            interventions.append("mask_pii_phone")

    # Rule 4: CITATION - Record, do NOT block
    has_citations = "[" in current_text and "]" in current_text
    missing_citations = has_retrieved_knowledge and not has_citations

    return OutputVerdict(
        text=current_text,
        da_can_thiep=tuple(interventions),
        loai_bi_mat=tuple(secrets_found),
        loai_ca_nhan=tuple(pii_found),
        thieu_trich_dan=missing_citations,
    )
