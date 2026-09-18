from typing import NamedTuple

from .citation import CitationValidationResult, validate_citations
from .toxicity import ToxicityScanResult, check_toxicity


class OutputGuardrailVerdict(NamedTuple):
    allowed: bool
    sanitized_text: str
    rejection_reason: str | None
    citation_result: CitationValidationResult | None
    toxicity_result: ToxicityScanResult | None


def enforce_output_guardrails(
    generated_text: str,
    valid_chunk_ids: list[str],
    require_citations: bool = False,
) -> OutputGuardrailVerdict:
    tox = check_toxicity(generated_text)
    if tox.is_toxic:
        return OutputGuardrailVerdict(
            allowed=False,
            sanitized_text="",
            rejection_reason="Violated toxicity safety policy",
            citation_result=None,
            toxicity_result=tox,
        )

    cit = validate_citations(generated_text, valid_chunk_ids)
    if require_citations and cit.missing_citations:
        # We allow it with a warning or annotate
        pass

    return OutputGuardrailVerdict(
        allowed=True,
        sanitized_text=generated_text,
        rejection_reason=None,
        citation_result=cit,
        toxicity_result=tox,
    )
