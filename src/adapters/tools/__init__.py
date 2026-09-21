"""Tool có chạm thế giới ngoài (HTTP, SQL, kho tri thức) — vì vậy nằm ở tầng adapter.

Việc đăng ký tool là hành động TƯỜNG MINH do composition root gọi, không phải
side effect lúc import: import một module không được phép làm thay đổi trạng thái
toàn cục, nếu không thứ tự import sẽ quyết định hành vi hệ thống.
"""

from .http_call import register_http_call_tool
from .poem_check import register_poem_check_tool
from .poem_quality import register_poem_quality_tool
from .search_kb import register_search_kb_tool
from .sql_query import register_sql_query_tool


def register_default_tools(retriever: object | None = None) -> None:
    """Nạp bộ tool mặc định vào sổ đăng ký. Gọi một lần khi dựng container."""
    register_search_kb_tool(retriever)  # type: ignore[arg-type]
    register_sql_query_tool()
    register_http_call_tool()
    register_poem_check_tool()
    register_poem_quality_tool()


__all__ = [
    "register_http_call_tool",
    "register_poem_check_tool",
    "register_poem_quality_tool",
    "register_search_kb_tool",
    "register_sql_query_tool",
    "register_default_tools",
]
