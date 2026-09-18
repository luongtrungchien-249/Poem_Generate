import re
from typing import Any

from application.agent.tools.registry import tool_registry

ALLOWED_TABLES = {"users_summary", "products", "orders", "daily_metrics", "documents"}
_DISALLOWED_KEYWORDS = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|GRANT|REVOKE|EXEC|CREATE)\b", re.IGNORECASE)


def register_sql_query_tool() -> None:
    @tool_registry.register(
        name="sql_query",
        description="Execute a safe, read-only SQL query against whitelisted analytical tables.",
        parameters_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL SELECT query to execute.",
                },
            },
            "required": ["query"],
        },
    )
    async def sql_query(query: str) -> dict[str, Any]:
        trimmed = query.strip()

        # 1. Enforce SELECT only
        if not trimmed.upper().startswith("SELECT"):
            return {"error": "Security violation: Only SELECT queries are permitted."}

        # 2. Check forbidden mutation keywords
        if _DISALLOWED_KEYWORDS.search(trimmed):
            return {"error": "Security violation: Mutating or dangerous SQL keywords detected."}

        # 3. Check table whitelist
        found_tables = set(re.findall(r"\bFROM\s+([a-zA-Z0-9_]+)", trimmed, re.IGNORECASE))
        for table in found_tables:
            if table.lower() not in ALLOWED_TABLES:
                return {"error": f"Security violation: Table '{table}' is not in the allowed list."}

        # Simulate safe read execution
        return {
            "columns": ["id", "metric_name", "value", "date"],
            "rows": [
                [1, "total_requests", 12500, "2026-09-16"],
                [2, "avg_latency_ms", 320, "2026-09-16"],
                [3, "error_rate_pct", 0.02, "2026-09-16"],
            ],
            "row_count": 3,
        }
