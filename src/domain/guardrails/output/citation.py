import re
from typing import NamedTuple


class CitationValidationResult(NamedTuple):
    has_citations: bool
    cited_ids: list[str]
    invalid_ids: list[str]
    missing_citations: bool


# Matches [chunk_id], [doc_id:chunk_id], [Nguồn: chunk_id]
_CITATION_REGEX = re.compile(r"\[(?:Nguồn:\s*)?([a-zA-Z0-9_\-:]+)\]")


def validate_citations(text: str, valid_chunk_ids: list[str]) -> CitationValidationResult:
    matches = _CITATION_REGEX.findall(text)
    cited_ids = list(set(matches))
    valid_set = set(valid_chunk_ids)

    invalid = [cid for cid in cited_ids if cid not in valid_set and ":" not in cid]
    has_citations = len(cited_ids) > 0
    missing = (len(valid_chunk_ids) > 0) and not has_citations

    return CitationValidationResult(
        has_citations=has_citations,
        cited_ids=cited_ids,
        invalid_ids=invalid,
        missing_citations=missing,
    )
