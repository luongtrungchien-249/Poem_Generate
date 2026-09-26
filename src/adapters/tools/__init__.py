"""Tool có chạm thế giới ngoài (HTTP, SQL, kho tri thức) — vì vậy nằm ở tầng adapter.

Việc đăng ký tool là hành động TƯỜNG MINH do composition root gọi, không phải
side effect lúc import: import một module không được phép làm thay đổi trạng thái
toàn cục, nếu không thứ tự import sẽ quyết định hành vi hệ thống.
"""

from .http_call import register_http_call_tool
from .poem_check import register_poem_check_tool
from .poem_generate import register_poem_generate_tool
from .poem_quality import register_poem_quality_tool
from .search_kb import register_search_kb_tool
from .sql_query import register_sql_query_tool


def register_default_tools(
    retriever: object | None = None,
    *,
    llm: object | None = None,
    tools: object | None = None,
    rate_limiter: object | None = None,
    default_model: str = "gpt-4o-mini",
    corpus: object | None = None,
) -> None:
    """Nạp bộ tool mặc định vào sổ đăng ký. Gọi một lần khi dựng container.

    `sinh_tho` cần ba phụ thuộc của đường sinh thơ. Thiếu chúng thì tool vẫn đăng
    ký nhưng báo lỗi rõ khi gọi — xem `poem_generate.py`. Im lặng bỏ qua sẽ khiến
    chat tưởng máy sinh thơ đã chạy và không có bài nào đạt.
    """
    register_search_kb_tool(retriever)  # type: ignore[arg-type]
    register_sql_query_tool()
    register_http_call_tool()
    register_poem_check_tool()
    register_poem_quality_tool()
    register_poem_generate_tool(llm, tools, rate_limiter, default_model, corpus)  # type: ignore[arg-type]


__all__ = [
    "register_http_call_tool",
    "register_poem_check_tool",
    "register_poem_generate_tool",
    "register_poem_quality_tool",
    "register_search_kb_tool",
    "register_sql_query_tool",
    "register_default_tools",
]
