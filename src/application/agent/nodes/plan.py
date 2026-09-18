from application.agent.state import AgentState
from application.ports.llm_client import LLMClient
from contracts.chat import Message, Role


class PlanNode:
    """Deconstructs the user goal into discrete, logical execution steps."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    async def execute(self, state: AgentState) -> AgentState:
        prompt = (
            f"Hãy lập kế hoạch gồm tối đa 3 bước ngắn gọn để giải quyết yêu cầu sau: '{state.query}'.\n"
            "Chỉ liệt kê các bước, mỗi bước trên 1 dòng bắt đầu bằng '- '."
        )
        resp = await self.llm_client.generate(
            messages=[Message(role=Role.USER, content=prompt)],
            model="mock-gpt",
        )
        lines = [line.strip("- ").strip() for line in resp.content.splitlines() if line.strip()]
        state.current_plan = lines or ["Tìm kiếm thông tin", "Tổng hợp câu trả lời"]
        state.step_index = 0
        return state
