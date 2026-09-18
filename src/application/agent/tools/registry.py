import inspect
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters_schema: dict[str, Any]
    func: Any = Field(exclude=True)


class ToolRegistry:
    """Manages agent tool definitions, schemas, and dynamic dispatch."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters_schema: dict[str, Any] | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            schema = parameters_schema or {
                "type": "object",
                "properties": {},
                "required": [],
            }
            self._tools[name] = ToolDefinition(
                name=name,
                description=description,
                parameters_schema=schema,
                func=func,
            )
            return func
        return decorator

    def get_tool(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters_schema,
            }
            for t in self._tools.values()
        ]

    async def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found in registry.")

        # Check if function is async
        if inspect.iscoroutinefunction(tool.func):
            return await tool.func(**arguments)
        return tool.func(**arguments)


tool_registry = ToolRegistry()
