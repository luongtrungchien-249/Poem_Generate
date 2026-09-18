from application.agent.state import AgentState


class ReflectNode:
    """Evaluates execution progress, detects tool errors, and decides next transition."""

    async def execute(self, state: AgentState) -> AgentState:
        last_result = state.tool_results[-1] if state.tool_results else None
        if last_result and last_result.is_error:
            state.reflection = f"Tool '{last_result.tool_name}' gặp lỗi: {last_result.result}. Cần chuyển hướng hoặc bỏ qua."
        else:
            state.reflection = f"Bước {state.step_index + 1} hoàn thành tốt. Có dữ liệu để trả lời."

        state.step_index += 1
        if state.step_index >= len(state.current_plan) or state.step_index >= state.max_steps:
            state.is_finished = True

        return state
