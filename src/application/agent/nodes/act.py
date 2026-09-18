import uuid

from application.agent.state import AgentState, ToolCallRecord, ToolResultRecord
from application.agent.tools.registry import tool_registry


class ActNode:
    """Selects and invokes the necessary tool based on the current plan step."""

    async def execute(self, state: AgentState) -> AgentState:
        if state.step_index >= len(state.current_plan):
            return state

        current_step_text = state.current_plan[state.step_index]

        # Simple semantic router to choose tool
        tool_name = "search_kb"
        args = {"query": state.query}
        if "sql" in current_step_text.lower() or "dữ liệu" in current_step_text.lower() or "bảng" in current_step_text.lower():
            tool_name = "sql_query"
            args = {"query": "SELECT * FROM daily_metrics LIMIT 5"}
        elif "http" in current_step_text.lower() or "api" in current_step_text.lower():
            tool_name = "http_call"
            args = {"url": "https://status.openai.com"}

        call_id = f"call_{uuid.uuid4().hex[:8]}"
        state.current_tool_calls.append(ToolCallRecord(id=call_id, name=tool_name, arguments=args))

        try:
            result = await tool_registry.execute(tool_name, args)
            state.tool_results.append(
                ToolResultRecord(call_id=call_id, tool_name=tool_name, result=result, is_error=False)
            )
        except Exception as e:
            state.tool_results.append(
                ToolResultRecord(call_id=call_id, tool_name=tool_name, result=str(e), is_error=True)
            )

        return state
