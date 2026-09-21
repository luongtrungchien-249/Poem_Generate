from typing import Any

from application.agent.tools.registry import tool_registry
from application.rag.retriever import HybridRetriever
from domain.conversation.tenant import TenantScope


def register_search_kb_tool(retriever: HybridRetriever | None = None) -> None:
    @tool_registry.register(
        name="search_kb",
        description="Search enterprise knowledge base for relevant documents, manuals, and internal policies.",
        parameters_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query keywords or question.",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of chunks to return (default: 3)",
                    "default": 3,
                },
            },
            "required": ["query"],
        },
    )
    async def search_kb(query: str, top_k: int = 3, tenant_id: str = "default") -> list[dict[str, Any]]:
        # Tool nhận `tenant_id` tường minh thay vì đọc biến toàn cục: sổ đăng ký
        # tool dùng chung cho mọi request, nên trạng thái toàn cục ở đây là đường
        # rò dữ liệu giữa các tenant chạy song song.
        if retriever:
            results = await retriever.retrieve(
                TenantScope(tenant_id=tenant_id), query=query, top_k=top_k
            )
            return [
                {
                    "chunk_id": r.chunk_id,
                    "content": r.content,
                    "score": r.score,
                    "metadata": r.metadata,
                }
                for r in results
            ]
        # Fallback simulated response
        return [
            {
                "chunk_id": "kb-001",
                "content": f"Thông tin tìm kiếm nội bộ liên quan tới: {query}",
                "score": 0.95,
                "metadata": {"title": "Internal KB"},
            }
        ]
