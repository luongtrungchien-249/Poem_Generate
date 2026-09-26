"""Cầu nối `LLMClient` (cũ) sang `LlmPort` (đường đi chính thức).

VÌ SAO CÓ FILE NÀY. Repo đang có hai định nghĩa "gọi mô hình là gì":

    ports/llm_client.py  LLMClient  — generate/stream/embed, dùng contracts.chat.Message
    ports/llm.py         LlmPort    — reply/cheap, dùng tagged union LlmMessage

ADR-0002 từng đề nghị HỢP NHẤT hai port. **ADR-0005 (21/09/2026) đã bác cách đặt
vấn đề đó**: ba nơi dùng `LLMClient` không phải hội thoại mà là `embed()` và
`stream()` — hai việc khác hẳn `reply()`. Ép chúng vào một Protocol thì mọi hiện
thực đều phải khai phương thức nó không dùng.

Vì vậy file này **ở lại**, không phải nợ chờ xoá: dịch giữa tagged union của
`LlmPort` và DTO Pydantic của provider là việc đúng của tầng adapter. Cái từng là
nợ thật — mất mát thông tin khi dịch — đã trả xong, xem mục dưới.

GỌI TOOL — ĐÃ THÔNG, 21/09/2026

Bản đầu của cầu này vứt bỏ `tools` và luôn trả `tool_calls=()`, nên vòng ReAct
không bao giờ gọi được `kiem_tra_tho`. Bốn tầng cùng chặn, đã sửa cả bốn:

    1. `LLMResponse` không có trường `tool_calls`   -> đã thêm
    2. adapter provider không GỬI `tools` đi        -> đã gửi
    3. adapter provider không ĐỌC `tool_calls` về   -> đã đọc
    4. cầu này vứt `tools` (`_ = tools`)            -> đã chuyển tiếp

Còn một tầng thứ năm ít ai ngờ: `content` của OpenAI là **null** khi mô hình chỉ
xin gọi tool, và `LLMResponse.content` khai kiểu `str` — nên ngay lần đầu mô hình
gọi tool thật, bản cũ sẽ nổ `ValidationError` chứ không âm thầm bỏ qua.
"""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

from application.ports.llm import (
    AssistantMessage,
    CallContext,
    CheapRoute,
    LlmMessage,
    LlmReply,
    LlmUsage,
    ToolCall,
    ToolMessage,
    UserMessage,
)
from application.ports.llm_client import LLMClient, ToolSchema
from application.ports.tools import ToolSpec
from contracts.chat import Message, Role
from domain.common.errors import BotError, UpstreamError
from domain.common.result import Err, Ok, Result


def _sang_message(m: LlmMessage) -> Message:
    """Đổi một lượt của `LlmPort` sang DTO mà `LLMClient` hiểu.

    🩸 LỖI ĐÃ SỬA. Bản đầu hạ `ToolMessage` xuống vai `user` và bọc nhãn văn bản:

        Message(role=USER, content="[ket_qua_tool call_1]\\n{...}")

    Cách đó ném mất `tool_call_id` vào bên trong một chuỗi. Hệ quả với API thật:
    lượt `assistant` xin gọi tool không có lượt `tool` nào ghép vào — OpenAI trả
    400, Anthropic cũng vậy. Và kể cả khi lọt, mô hình thấy kết quả tool như lời
    người dùng nói, nên không biết kết quả nào thuộc lời gọi nào.

    Nay dùng đúng `Role.TOOL` với `tool_call_id`. Cả hai trường ấy đã có sẵn trong
    `contracts.chat.Message` từ đầu — chỉ là chưa ai dùng tới.
    """
    if isinstance(m, UserMessage):
        return Message(role=Role.USER, content=m.content)
    if isinstance(m, AssistantMessage):
        return Message(
            role=Role.ASSISTANT,
            content=m.content,
            tool_calls=[
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": tc.arguments},
                }
                for tc in m.tool_calls
            ]
            or None,
        )
    if isinstance(m, ToolMessage):
        return Message(role=Role.TOOL, content=m.content, tool_call_id=m.tool_call_id)
    raise TypeError(f"Lượt hội thoại lạ: {type(m).__name__}")


def _sang_luoc_do_tool(t: object) -> ToolSchema | None:
    """`ToolSpec` -> lược đồ trung lập. Thứ lạ thì BỎ QUA, không làm hỏng lượt gọi.

    `LlmPort.reply` khai `tools: tuple[Any, ...]`, nên về nguyên tắc có thể nhận
    bất cứ thứ gì. Ném ngoại lệ ở đây sẽ biến một tool khai sai thành một lượt hội
    thoại chết; bỏ qua thì mô hình chỉ mất một công cụ, và vòng ngoài vẫn bảo đảm.
    """
    if isinstance(t, ToolSpec):
        return {"name": t.name, "description": t.description, "parameters": t.parameters}
    if isinstance(t, dict) and "name" in t:
        return {
            "name": t["name"],
            "description": t.get("description", ""),
            "parameters": t.get("parameters", {}),
        }
    return None


# ════ THỬ LẠI LỖI TẠM THỜI — QĐ-P9, Plan_PoeTone, 26/09/2026 ════
#
# Đo thật: tài khoản có trần 200.000 token/phút, một bài 20 dòng gửi tới 8 lượt
# song song. Không thử lại thì 8/20 đề của lượt đo đầu trượt OAN — không phải vì
# thơ sai luật, mà vì nhà cung cấp bảo "chờ chút". Trả 422 cho người dùng trong ca
# đó là nói dối về lý do thất bại.
#
# CHỈ thử lại lỗi TẠM THỜI: 429 và 5xx, cộng lỗi mạng. 400/401/404 là lỗi của
# chính yêu cầu — gửi lại y hệt chỉ nhận lại y hệt, và tốn thêm thời gian của người
# dùng. `FallbackManager` ở `resilience.py` thử lại MỌI ngoại lệ nên không dùng ở đây.
#
# Không phải ngưỡng dò chất lượng: mấy hằng số dưới đây chỉ quyết định chờ bao lâu
# trước khi bỏ cuộc, không đụng tới luật hay tới việc bài nào được trả ra.
SO_LAN_THU_LAI = 6
CHO_TOI_DA_GIAY = 60.0
_MA_TAM_THOI = frozenset({429, 500, 502, 503, 504})


def _ma_trang_thai(e: BaseException) -> int | None:
    return e.response.status_code if isinstance(e, httpx.HTTPStatusError) else None


def _la_loi_tam_thoi(e: BaseException) -> bool:
    ma = _ma_trang_thai(e)
    if ma is not None:
        return ma in _MA_TAM_THOI
    return isinstance(e, (httpx.TimeoutException, httpx.TransportError))


def _thoi_gian_cho(e: BaseException, lan: int) -> float:
    """Ưu tiên `Retry-After` của nhà cung cấp; không có thì backoff mũ + jitter."""
    if isinstance(e, httpx.HTTPStatusError):
        tieu_de = e.response.headers.get("retry-after")
        try:
            if tieu_de is not None:
                return min(CHO_TOI_DA_GIAY, max(0.0, float(tieu_de)))
        except ValueError:
            pass
    return min(CHO_TOI_DA_GIAY, 2.0 * 2**lan) + random.uniform(0, 1)


class ChatLlmAdapter:
    """Hiện thực `LlmPort` bằng một `LLMClient` bất kỳ."""

    def __init__(
        self,
        client: LLMClient,
        *,
        default_model: str = "gpt-4o-mini",
        so_lan_thu_lai: int = SO_LAN_THU_LAI,
        ngu: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._client = client
        self._default_model = default_model
        self._so_lan_thu_lai = so_lan_thu_lai
        # Tiêm được để test không phải chờ thật.
        self._ngu = ngu

    async def reply(
        self,
        messages: tuple[LlmMessage, ...],
        tools: tuple[Any, ...],
        ctx: CallContext,
        model: str | None = None,
    ) -> Result[LlmReply, BotError]:
        luoc_do = [x for x in (_sang_luoc_do_tool(t) for t in tools) if x is not None]
        lan = 0
        while True:
            try:
                resp = await self._client.generate(
                    messages=[_sang_message(m) for m in messages],
                    model=model or self._default_model,
                    tools=luoc_do or None,
                )
                break
            except Exception as e:  # noqa: BLE001 — biên với thế giới ngoài
                if _la_loi_tam_thoi(e) and lan < self._so_lan_thu_lai:
                    await self._ngu(_thoi_gian_cho(e, lan))
                    lan += 1
                    continue
                # Mọi lỗi provider quy về một lỗi nghiệp vụ CÓ PHÂN LOẠI. Để ngoại
                # lệ thô đi lên sẽ phá hợp đồng `Result` của cả đường ống.
                return Err(UpstreamError(
                    upstream=type(self._client).__name__,
                    status_code=_ma_trang_thai(e),
                    message=str(e),
                ))

        usage = resp.usage or {}
        return Ok(
            LlmReply(
                text=resp.content,
                tool_calls=tuple(
                    ToolCall(id=tc.id, name=tc.name, arguments=tc.arguments)
                    for tc in resp.tool_calls
                ),
                usage=LlmUsage(
                    input_tokens=int(usage.get("prompt_tokens", 0)),
                    output_tokens=int(usage.get("completion_tokens", 0)),
                ),
            )
        )

    async def cheap(
        self,
        messages: tuple[LlmMessage, ...],
        route: CheapRoute,
        ctx: CallContext,
    ) -> Result[str, BotError]:
        kq = await self.reply(messages, (), ctx)
        return Ok(kq.value.text) if isinstance(kq, Ok) else Err(kq.error)
