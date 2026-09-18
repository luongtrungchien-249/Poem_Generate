"""Sổ đăng ký tool — thuần khai báo. Hiện thực có I/O nằm ở `adapters/tools/`."""

from .registry import ToolDefinition, ToolRegistry, tool_registry

__all__ = ["ToolRegistry", "ToolDefinition", "tool_registry"]
