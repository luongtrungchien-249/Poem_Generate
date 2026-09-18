from typing import Any
from urllib.parse import urlparse

import httpx

from application.agent.tools.registry import tool_registry

ALLOWED_DOMAINS = {"api.github.com", "httpbin.org", "status.openai.com", "api.internal.local"}


def register_http_call_tool() -> None:
    @tool_registry.register(
        name="http_call",
        description="Make a secure HTTP GET request to an approved external API domain.",
        parameters_schema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch (must be from allowed domains).",
                },
            },
            "required": ["url"],
        },
    )
    async def http_call(url: str) -> dict[str, Any]:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""

        if hostname not in ALLOWED_DOMAINS:
            return {
                "error": f"Security violation: Domain '{hostname}' is not in the outbound allowlist."
            }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                body = resp.text[:4000] # truncate
                return {
                    "status_code": resp.status_code,
                    "content": body,
                }
        except Exception as e:
            return {"error": f"HTTP request failed: {str(e)}"}
