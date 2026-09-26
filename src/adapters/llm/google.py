"""Google AI (Gemini API) provider — phục vụ cả Gemini lẫn Gemma.

════ VÌ SAO ADAPTER NÀY RA ĐỜI, 22/09/2026 ════

Chủ dự án ghép `prompting/system.py` + `prompting/instructions.py` thành System
Instruction, đưa cho Gemma trên Google AI platform, sinh 200 bài. Đối chiếu qua
`rule.py`: **1/200 đạt (0,50 %)**.

Nguyên nhân KHÔNG phải mô hình kém. Hai file ấy **cố ý không chứa một chữ luật thơ
nào** — có test cưỡng chế. Luật nằm ở `poetry/prompt.py::CHI_DAN_SINH_THO`, sinh ra
từ `rule.LUAT` lúc import. Nên Gemma chưa bao giờ được cho biết bài thơ phải như
thế nào, mà vẫn viết đúng 7 tiếng ở 98,9 % số dòng.

Adapter này để Gemma chạy BÊN TRONG đường ống — nơi nó nhận đủ prompt, được sinh
theo từng khổ, chọn trong nhiều ứng viên, và đi qua cổng bảy tầng. Đo thật 21/09
trên `gpt-4o-mini`: một lượt gọi cả bài 8,3 % · qua `sinh_theo_kho` 83,3 %.

════ KHÁC OPENAI Ở NĂM CHỖ, DỊCH HẾT TRONG FILE NÀY ════

    thân yêu cầu   `contents: [{role, parts:[{text}]}]`  không phải `messages`
    vai assistant  `"model"`                             không phải `"assistant"`
    lượt system    trường riêng `systemInstruction`      không nằm trong `contents`
    tool           `tools:[{functionDeclarations:[...]}]` không bọc `{"type":"function"}`
    xác thực       header `x-goog-api-key`               không phải Bearer

⚠️ CHƯA DÙNG ĐƯỢC CHO /v1/chat. Chủ dự án chốt 23/09/2026 quay về `gpt-4o-mini`,
nên adapter này ở trạng thái SẴN SÀNG NHƯNG KHÔNG ĐƯỢC CHỌN — giống `AnthropicClient`
và `VLLMClient`. Bật lại chỉ cần đổi `DEFAULT_PROVIDER`.

Nhưng bật xong thì đường CHAT vẫn hỏng, và đó KHÔNG phải lỗi của file này:
`/v1/chat` chọn model qua `ModelRouter.select_model`, mà bảng `tiers` trong
`configs/models.yaml` trỏ cứng vào `gpt-4o-mini` / `gpt-4o` / `o1-preview` —
không có một model Google nào. Kết quả: `models/gpt-4o-mini:generateContent`
gửi tới Google  ->  404, mọi lượt chat.

`/v1/poem` thì chạy được, vì nó dùng thẳng `container.default_model` chứ không
qua router. Muốn dùng Google cho cả hai đường thì phải khai model Google trong
`configs/models.yaml` và cho `tiers` trỏ theo provider đang bật — đó là lỗi
kiến trúc chung, không riêng Google: đổi provider nào cũng gãy đường chat.

⚠️ GEMMA CÓ THỂ KHÔNG GỌI ĐƯỢC TOOL. Function calling là tính năng của dòng Gemini;
các model Gemma phục vụ qua cùng endpoint nhiều khả năng không có. Hệ thống đã tự
xuống thang đúng cách: `sinh_theo_kho._chon_mot_kho` chỉ chạy bước cứu ReAct khi
`tools is not None`, nên thiếu tool thì mất bước cứu chứ không gãy. Xem
`ho_tro_tool()` ở cuối file — kiểm bằng một lượt gọi thật, đừng đoán.
"""

import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

from adapters.observability.cost import cost_calculator
from application.ports.llm_client import (
    LLMResponse,
    LLMStreamChunk,
    ToolCallOut,
    ToolSchema,
)
from contracts.chat import Message

# Model nhúng mặc định của Google AI. Tách hằng số vì nó KHÁC model sinh — dùng
# nhầm model sinh cho `:embedContent` sẽ nhận 400 mà thông báo không nói rõ.
MODEL_NHUNG_MAC_DINH = "models/text-embedding-004"

# Tiền tố bắt buộc của Gemini API. `gemma-3-27b-it` phải thành `models/gemma-3-27b-it`
# trên đường dẫn; truyền tên trần là 404.
_TIEN_TO_MODEL = "models/"


def _duong_dan_model(model: str) -> str:
    """Chuẩn hoá tên model về dạng `models/<ten>` mà Gemini API đòi."""
    return model if model.startswith(_TIEN_TO_MODEL) else f"{_TIEN_TO_MODEL}{model}"


def _sang_tool_google(t: ToolSchema) -> dict[str, Any]:
    """Lược đồ trung lập -> `functionDeclarations` của Google.

    Cùng ba khoá với OpenAI (`name`, `description`, `parameters`) nhưng KHÔNG bọc
    trong `{"type": "function"}`, và cả danh sách nằm dưới MỘT phần tử `tools`.
    """
    return {
        "name": t["name"],
        "description": t.get("description", ""),
        "parameters": t.get("parameters") or {"type": "object", "properties": {}},
    }


def _sang_luot_google(m: Message) -> dict[str, Any]:
    """Đổi một `Message` sang một phần tử `contents`.

    GOOGLE KHÁC OPENAI Ở CHỖ NÀY:

      - Không có vai `tool`. Kết quả tool là một lượt **user** chứa phần
        `functionResponse`, ghép bằng TÊN HÀM chứ không bằng id.
      - Lời xin gọi tool là một lượt **model** chứa phần `functionCall`.
      - Vai `assistant` gọi là `model`.

    Ghép bằng tên hàm là điểm yếu của định dạng này: hai lời gọi cùng một hàm
    trong một lượt thì không phân biệt được kết quả nào của lời gọi nào. Không có
    cách nào sửa ở phía adapter — Google không nhận id — nên ghi ra đây để người
    đọc biết giới hạn thay vì tưởng nó tương đương Anthropic.
    """
    vai = m.role.value

    if vai == "tool":
        try:
            ket_qua = json.loads(m.content) if m.content else {}
        except json.JSONDecodeError:
            # Không phải JSON thì bọc lại — `response` bắt buộc là object.
            ket_qua = {"ket_qua": m.content}
        return {
            "role": "user",
            "parts": [
                {
                    "functionResponse": {
                        "name": m.name or m.tool_call_id or "",
                        "response": ket_qua if isinstance(ket_qua, dict) else {"ket_qua": ket_qua},
                    }
                }
            ],
        }

    if vai == "assistant" and m.tool_calls:
        parts: list[dict[str, Any]] = []
        if m.content:
            parts.append({"text": m.content})
        for tc in m.tool_calls:
            ham = tc.get("function", tc)
            tham_so = ham.get("arguments", "{}")
            try:
                doi_so = json.loads(tham_so) if isinstance(tham_so, str) else tham_so
            except json.JSONDecodeError:
                # Tham số hỏng thì gửi nguyên văn, để mô hình thấy lại đúng thứ nó
                # đã viết thay vì thấy một object rỗng.
                doi_so = {"_raw": tham_so}
            parts.append({"functionCall": {"name": ham.get("name", ""), "args": doi_so}})
        return {"role": "model", "parts": parts}

    return {
        "role": "user" if vai == "user" else "model",
        "parts": [{"text": m.content or ""}],
    }


def _doc_phan_hoi(data: dict[str, Any], model: str) -> LLMResponse:
    """Rút nội dung và lời gọi tool từ một `generateContent` response.

    THUẦN — tách khỏi lời gọi mạng để test được mà không cần API thật.
    """
    ung_vien = (data.get("candidates") or [{}])[0]
    parts = (ung_vien.get("content") or {}).get("parts") or []

    content = "".join(p.get("text", "") for p in parts if "text" in p)

    tool_calls: list[ToolCallOut] = []
    for i, p in enumerate(parts):
        fc = p.get("functionCall")
        if not fc:
            continue
        # Google KHÔNG cấp id cho lời gọi tool. Dựng id tại chỗ theo thứ tự xuất
        # hiện, vì `ToolCallOut.id` là bắt buộc và vòng ReAct dùng nó để ghép kết
        # quả. Id này chỉ sống trong một lượt, không gửi ngược lên Google.
        tool_calls.append(
            ToolCallOut(
                id=f"{fc.get('name', 'tool')}-{i}",
                name=fc.get("name", ""),
                arguments=json.dumps(fc.get("args", {}), ensure_ascii=False),
            )
        )

    usage = data.get("usageMetadata", {})
    prompt_tokens = usage.get("promptTokenCount", 0)
    completion_tokens = usage.get("candidatesTokenCount", 0)

    return LLMResponse(
        content=content,
        model=model,
        finish_reason=ung_vien.get("finishReason", "STOP"),
        usage={"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens},
        cost_usd=cost_calculator.calculate_cost(model, prompt_tokens, completion_tokens),
        raw_response=data,
        tool_calls=tool_calls,
    )


class GoogleAIClient:
    """Google AI (Gemini API) provider — dùng được cho cả Gemini lẫn Gemma."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
    ) -> None:
        # Khoá và endpoint do composition root truyền vào; adapter KHÔNG đọc môi
        # trường — quy tắc chung của tầng này, xem `anthropic.py`.
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        # Dùng header thay vì `?key=` trên query string: khoá lọt vào URL là lọt
        # vào log truy cập của mọi proxy trên đường đi.
        return {"x-goog-api-key": self.api_key, "Content-Type": "application/json"}

    def _than_yeu_cau(
        self,
        messages: list[Message],
        temperature: float,
        max_tokens: int | None,
        tools: list[ToolSchema] | None,
        them: dict[str, Any],
    ) -> dict[str, Any]:
        """Dựng payload. Tách ra để `generate` và `stream` không lệch nhau."""
        loi_he_thong = next((m.content for m in messages if m.role.value == "system"), None)
        contents = [_sang_luot_google(m) for m in messages if m.role.value != "system"]

        cau_hinh: dict[str, Any] = {"temperature": temperature}
        if max_tokens:
            cau_hinh["maxOutputTokens"] = max_tokens

        payload: dict[str, Any] = {"contents": contents, "generationConfig": cau_hinh}
        if loi_he_thong:
            payload["systemInstruction"] = {"parts": [{"text": loi_he_thong}]}
        if tools:
            # Cả danh sách nằm dưới MỘT phần tử, khác OpenAI (mỗi tool một phần tử).
            payload["tools"] = [{"functionDeclarations": [_sang_tool_google(t) for t in tools]}]
        payload.update(them)
        return payload

    async def generate(
        self,
        messages: list[Message],
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[ToolSchema] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        payload = self._than_yeu_cau(messages, temperature, max_tokens, tools, kwargs)

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/{_duong_dan_model(model)}:generateContent",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        return _doc_phan_hoi(data, model)

    async def stream(
        self,
        messages: list[Message],
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[LLMStreamChunk]:
        payload = self._than_yeu_cau(messages, temperature, max_tokens, None, kwargs)

        async with httpx.AsyncClient(timeout=60.0) as client, client.stream(
            "POST",
            # `alt=sse` bắt buộc: thiếu nó Google trả một mảng JSON lớn chứ không
            # phải luồng sự kiện, và vòng đọc dưới đây sẽ không thấy dòng nào.
            f"{self.base_url}/{_duong_dan_model(model)}:streamGenerateContent?alt=sse",
            headers=self._headers(),
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                try:
                    parsed = json.loads(line[6:].strip())
                except json.JSONDecodeError:
                    continue
                ung_vien = (parsed.get("candidates") or [{}])[0]
                parts = (ung_vien.get("content") or {}).get("parts") or []
                delta = "".join(p.get("text", "") for p in parts if "text" in p)
                if delta:
                    yield LLMStreamChunk(delta=delta)
                if ung_vien.get("finishReason"):
                    yield LLMStreamChunk(delta="", finish_reason="stop")

    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        """Nhúng qua `:batchEmbedContents`.

        Model nhúng KHÁC model sinh — mặc định `text-embedding-004`. Truyền nhầm
        tên model sinh vào đây sẽ nhận 400 với thông báo không nói rõ nguyên nhân.
        """
        ten = _duong_dan_model(model or MODEL_NHUNG_MAC_DINH)
        payload = {
            "requests": [
                {"model": ten, "content": {"parts": [{"text": t}]}} for t in texts
            ]
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/{ten}:batchEmbedContents",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        return [e.get("values", []) for e in data.get("embeddings", [])]

    async def ho_tro_tool(self, model: str) -> bool:
        """Model này có gọi được tool không — KIỂM bằng một lượt gọi thật.

        ⚠️ ĐỪNG ĐOÁN TỪ TÊN MODEL. Function calling là tính năng của dòng Gemini;
        Gemma phục vụ qua cùng endpoint nhiều khả năng không có. Nhưng danh sách
        model đổi theo thời gian, nên câu trả lời đúng chỉ đến từ một lượt gọi.

        Dùng ở bước dựng hệ thống để quyết có truyền `tools` cho đường sinh thơ hay
        không: thiếu tool thì `sinh_theo_kho` mất bước cứu ReAct, nhưng vẫn chạy.
        """
        thu: ToolSchema = {
            "name": "ping",
            "description": "Hàm thử, không làm gì",
            "parameters": {"type": "object", "properties": {}},
        }
        try:
            await self.generate(
                messages=[Message(role="user", content="xin chào")],  # type: ignore[arg-type]
                model=model,
                max_tokens=16,
                tools=[thu],
            )
        except httpx.HTTPStatusError:
            # 400 ở đây gần như luôn là "model không nhận trường tools".
            return False
        return True
