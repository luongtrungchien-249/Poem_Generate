import pytest

from adapters.llm.mock import MockLLMClient
from adapters.tools import register_default_tools
from application.agent.graph import AgentGraph
from application.agent.tools.registry import tool_registry


@pytest.fixture(autouse=True)
def _dang_ky_tool_mac_dinh():
    # Tool được nạp tường minh, không còn dựa vào side effect lúc import.
    register_default_tools()


@pytest.mark.asyncio
async def test_agent_graph_execution():
    mock_llm = MockLLMClient()
    graph = AgentGraph(llm_client=mock_llm)

    state = await graph.run(query="Tìm kiếm thông tin về bảo mật dữ liệu doanh nghiệp", max_steps=2)
    assert state.is_finished
    assert len(state.current_plan) > 0
    assert len(state.tool_results) > 0
    assert state.final_response is not None


@pytest.mark.asyncio
async def test_safe_sql_tool():
    # Safe SELECT query
    res = await tool_registry.execute("sql_query", {"query": "SELECT * FROM daily_metrics LIMIT 2"})
    assert "error" not in res
    assert res.get("row_count") == 3

    # Forbidden DROP query
    res_drop = await tool_registry.execute("sql_query", {"query": "DROP TABLE users;"})
    assert "error" in res_drop

    # Forbidden table query
    res_table = await tool_registry.execute("sql_query", {"query": "SELECT * FROM private_passwords;"})
    assert "error" in res_table
