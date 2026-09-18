import re

_TAG_LOOKALIKE = re.compile(r"</?(tai_lieu|context|tool_result|fact|prompt)[^>]*>", re.IGNORECASE)


def sanitize_tag_lookalikes(content: str) -> str:
    """Strips fake closing or opening XML tag lookalikes to prevent prompt escape attacks."""
    return _TAG_LOOKALIKE.sub("", content)


def wrap_xml_tag(tag_name: str, content: str, attributes: str = "") -> str:
    """Wraps untrusted content in an XML tag after sanitizing self-closing lookalikes."""
    sanitized = sanitize_tag_lookalikes(content)
    attr_str = f" {attributes}" if attributes else ""
    return f"<{tag_name}{attr_str}>\n{sanitized}\n</{tag_name}>"
