from application.agent.state import AgentState
from application.ports.llm_client import LLMClient
from contracts.chat import Message, Role


class FinalizeNode:
    """Synthesizes the trajectory results and tool findings into a coherent final answer."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    async def execute(self, state: AgentState) -> AgentState:
        findings = [f"- {res.tool_name}: {res.result}" for res in state.tool_results]
        findings_text = "\n".join(findings) if findings else "Không có kết quả công cụ."

        prompt = (
            f"Câu hỏi của người dùng: {state.query}\n\n"
            f"Kết quả thu thập được:\n{findings_text}\n\n"
            "Hãy tổng hợp câu trả lời chi tiết, chính xác và có cấu trúc rõ ràng."
        )
        resp = await self.llm_client.generate(
            messages=[Message(role=Role.USER, content=prompt)],
            model="mock-gpt",
        )
        state.final_response = resp.content
        state.is_finished = True
        return state
