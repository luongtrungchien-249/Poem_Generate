"""Hiện thực `ToolPort` trên sổ đăng ký tool.

`call_many` chứ không phải `call`: mô hình thường xin nhiều tool trong một lượt, và
chạy tuần tự thì độ trễ cộng dồn vô cớ. Chữ ký số nhiều cũng chặn luôn một cám dỗ —
cắt bớt lời gọi rồi ghi lại như thể mô hình chỉ xin bấy nhiêu.

MỌI LỖI TOOL ĐỀU LÀ DỮ LIỆU, KHÔNG PHẢI NGOẠI LỆ. Một tool hỏng không được phép
giết cả lượt: mô hình cần *biết* nó hỏng để đổi cách, nên lỗi quay về dưới dạng
`ToolResult(is_error=True)` với nội dung đọc được.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from application.agent.tools.registry import ToolRegistry, tool_registry
from application.ports.llm import CallContext, ToolCall, ToolResult
from application.ports.tools import ToolSpec

# Trần thời gian cho MỘT lời gọi tool. Tool trong repo này đều thuần và chạy trong
# mili-giây; trần đặt ở đây để một tool HTTP thêm sau không treo cả lượt.
TRAN_GIAY_MOI_TOOL = 5.0


class RegistryToolExecutor:
    """`ToolPort` đọc từ `tool_registry`."""

    def __init__(
        self, registry: ToolRegistry | None = None, *, timeout_sec: float = TRAN_GIAY_MOI_TOOL
    ) -> None:
        self._registry = registry or tool_registry
        self._timeout = timeout_sec

    def specs(self) -> tuple[ToolSpec, ...]:
        return tuple(
            ToolSpec(name=t["name"], description=t["description"], parameters=t["parameters"])
            for t in self._registry.list_tools()
        )

    async def call_many(
        self, calls: tuple[ToolCall, ...], ctx: CallContext
    ) -> tuple[ToolResult, ...]:
        if not calls:
            return ()
        ket_qua = await asyncio.gather(*(self._goi_mot(c) for c in calls))
        return tuple(ket_qua)

    async def _goi_mot(self, call: ToolCall) -> ToolResult:
        try:
            tham_so = json.loads(call.arguments) if call.arguments.strip() else {}
        except json.JSONDecodeError as e:
            return ToolResult(
                call_id=call.id,
                content=f"Tham số không phải JSON hợp lệ: {e}",
                is_error=True,
            )
        if not isinstance(tham_so, dict):
            return ToolResult(
                call_id=call.id,
                content="Tham số phải là một object JSON.",
                is_error=True,
            )

        try:
            gia_tri: Any = await asyncio.wait_for(
                self._registry.execute(call.name, tham_so), timeout=self._timeout
            )
        except TimeoutError:
            return ToolResult(
                call_id=call.id,
                content=f"Tool '{call.name}' quá {self._timeout}s chưa trả lời.",
                is_error=True,
            )
        except Exception as e:  # noqa: BLE001 — biên với mã tool bên ngoài
            return ToolResult(
                call_id=call.id, content=f"Tool '{call.name}' lỗi: {e}", is_error=True
            )

        noi_dung = (
            gia_tri
            if isinstance(gia_tri, str)
            else json.dumps(gia_tri, ensure_ascii=False, default=str)
        )
        return ToolResult(call_id=call.id, content=noi_dung)
