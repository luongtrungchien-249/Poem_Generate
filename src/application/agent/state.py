from typing import Any

from pydantic import BaseModel, Field

from contracts.chat import Message


class ToolCallRecord(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any]


class ToolResultRecord(BaseModel):
    call_id: str
    tool_name: str
    result: Any
    is_error: bool = False


class AgentState(BaseModel):
    """Serializable agent execution state tracking the reasoning trajectory."""

    messages: list[Message] = Field(default_factory=list)
    query: str = ""
    current_plan: list[str] = Field(default_factory=list)
    step_index: int = 0
    max_steps: int = 5
    current_tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    tool_results: list[ToolResultRecord] = Field(default_factory=list)
    reflection: str | None = None
    final_response: str | None = None
    is_finished: bool = False
    error: str | None = None
    scratchpad: dict[str, Any] = Field(default_factory=dict)
