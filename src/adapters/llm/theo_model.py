"""`LLMClient` ĐỊNH TUYẾN THEO TÊN MODEL — dùng nhiều khoá cùng lúc (OpenAI + Gemini + …).

    gemini-2.5-flash  -> GoogleAIClient
    gpt-4o-mini       -> OpenAIClient
    claude-3-5-haiku  -> AnthropicClient

Trước đây `_build_llm` dựng ĐÚNG MỘT client theo `DEFAULT_PROVIDER`. Mọi model khác
provider — kể cả model dự phòng trong `tiers` của `models.yaml` — đều bị gửi tới
provider sai, và nhận 404 với thông báo không nói rõ vì sao.

════ TÌM PROVIDER CỦA MỘT MODEL ════

    1. `configs/models.yaml` khai `provider` cho model đó      -> dùng nó
    2. không có trong danh mục -> đoán theo TIỀN TỐ tên       -> `_TIEN_TO`
    3. vẫn không biết                                         -> provider mặc định

Provider tìm được mà KHÔNG có khoá -> ném `ChuaCoKhoaProvider` ngay, không gửi đi
đâu. `FallbackManager` của đường chat bắt ngoại lệ đó và thử model kế tiếp; đường
thơ nhận nó thành `UpstreamError` có thông báo rõ.

Adapter này không import adapter nào khác (hợp đồng "Cac adapter khong goi lan
nhau"): các client con do composition root dựng rồi truyền vào.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Any

from application.ports.generation import LLMResponse, ToolSchema
from application.ports.llm_client import LLMClient
from application.ports.streaming import LLMStreamChunk
from contracts.chat import Message

_TIEN_TO: tuple[tuple[str, str], ...] = (
    ("gemini", "google"),
    ("gemma", "google"),
    ("models/", "google"),
    ("gpt-", "openai"),
    ("o1", "openai"),
    ("o3", "openai"),
    ("o4", "openai"),
    ("claude", "anthropic"),
    ("mock", "mock"),
)


class ChuaCoKhoaProvider(RuntimeError):
    """Model thuộc một provider chưa được cấu hình khoá."""


class LLMClientTheoModel:
    def __init__(
        self,
        clients: Mapping[str, LLMClient],
        *,
        provider_mac_dinh: str,
        model_mac_dinh: str,
        provider_cua_model: Mapping[str, str] | None = None,
    ) -> None:
        if provider_mac_dinh not in clients:
            raise ValueError(f"provider mặc định {provider_mac_dinh!r} không có client")
        self._clients = dict(clients)
        self._mac_dinh = provider_mac_dinh
        self._model_mac_dinh = model_mac_dinh
        self._danh_muc = dict(provider_cua_model or {})

    @property
    def cac_provider(self) -> tuple[str, ...]:
        return tuple(self._clients)

    def provider_cho(self, model: str | None) -> str:
        if not model:
            return self._mac_dinh
        if model in self._danh_muc:
            return self._danh_muc[model]
        ten = model.lower()
        for tien_to, provider in _TIEN_TO:
            if ten.startswith(tien_to):
                return provider
        return self._mac_dinh

    def _client_cho(self, model: str) -> LLMClient:
        provider = self.provider_cho(model)
        client = self._clients.get(provider)
        if client is None:
            raise ChuaCoKhoaProvider(
                f"Model {model!r} thuộc provider {provider!r}, nhưng chưa có khoá cho "
                f"provider đó (có: {', '.join(self._clients)})."
            )
        return client

    async def generate(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[ToolSchema] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        ten = model or self._model_mac_dinh
        return await self._client_cho(ten).generate(
            messages, model=ten, temperature=temperature, max_tokens=max_tokens,
            tools=tools, **kwargs,
        )

    async def stream(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[LLMStreamChunk]:
        ten = model or self._model_mac_dinh
        async for manh in self._client_cho(ten).stream(
            messages, model=ten, temperature=temperature, max_tokens=max_tokens, **kwargs
        ):
            yield manh

    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        # Nhúng dùng model nhúng của provider — tên model sinh không áp dụng ở đây.
        # Không truyền model thì đi provider mặc định, giữ nguyên hành vi cũ của RAG.
        client = self._client_cho(model) if model else self._clients[self._mac_dinh]
        return await client.embed(texts, model=model)
