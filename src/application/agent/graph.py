from application.agent.nodes.act import ActNode
from application.agent.nodes.finalize import FinalizeNode
from application.agent.nodes.plan import PlanNode
from application.agent.nodes.reflect import ReflectNode
from application.agent.state import AgentState
from application.ports.llm_client import LLMClient
from application.ports.tracer import NullTracer, TracerPort


class AgentGraph:
    """Cyclic state graph coordinating Plan-Act-Reflect-Finalize agent workflows."""

    def __init__(self, llm_client: LLMClient, tracer: TracerPort | None = None) -> None:
        self.tracer: TracerPort = tracer or NullTracer()
        self.plan_node = PlanNode(llm_client)
        self.act_node = ActNode()
        self.reflect_node = ReflectNode()
        self.finalize_node = FinalizeNode(llm_client)

    async def run(self, query: str, max_steps: int = 4) -> AgentState:
        state = AgentState(query=query, max_steps=max_steps)

        with self.tracer.span("agent_graph_execution", {"query": query}):
            # 1. Plan
            with self.tracer.span("agent_node_plan"):
                state = await self.plan_node.execute(state)

            # 2. Cyclic Act-Reflect loop
            while not state.is_finished:
                with self.tracer.span("agent_node_act", {"step": state.step_index}):
                    state = await self.act_node.execute(state)

                with self.tracer.span("agent_node_reflect", {"step": state.step_index}):
                    state = await self.reflect_node.execute(state)

            # 3. Finalize
            with self.tracer.span("agent_node_finalize"):
                state = await self.finalize_node.execute(state)

        return state
