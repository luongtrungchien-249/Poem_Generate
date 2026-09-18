import json
from typing import Any, NamedTuple


class SchemaValidationResult(NamedTuple):
    is_valid: bool
    parsed_data: dict[str, Any] | None
    error: str | None


def validate_json_output(output_text: str) -> SchemaValidationResult:
    """Attempts to extract and parse JSON from LLM output (supporting markdown backtick blocks)."""
    text = output_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        data = json.loads(text)
        return SchemaValidationResult(is_valid=True, parsed_data=data, error=None)
    except Exception as e:
        return SchemaValidationResult(is_valid=False, parsed_data=None, error=str(e))
