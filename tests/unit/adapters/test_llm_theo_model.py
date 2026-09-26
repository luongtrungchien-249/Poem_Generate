"""Nhiều khoá cùng lúc: mỗi model đi đúng nhà cung cấp của nó."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.llm.router import ModelRouter
from adapters.llm.theo_model import ChuaCoKhoaProvider, LLMClientTheoModel
from application.ports.generation import LLMResponse

pytestmark = pytest.mark.unit

CATALOG = Path(__file__).resolve().parents[3] / "configs" / "models.yaml"


class _Gia:
    def __init__(self, ten: str) -> None:
        self.ten = ten
        self.goi: list[str] = []

    async def generate(self, messages, model, **kw):  # type: ignore[no-untyped-def]
        self.goi.append(model)
        return LLMResponse(content=self.ten, model=model)

    async def stream(self, messages, model, **kw):  # type: ignore[no-untyped-def]
        yield None

    async def embed(self, texts, model=None):  # type: ignore[no-untyped-def]
        return [[float(len(self.ten))]]


def _router(**clients):  # type: ignore[no-untyped-def]
    return LLMClientTheoModel(
        clients, provider_mac_dinh="openai", model_mac_dinh="gpt-4o-mini",
        provider_cua_model={"model-la": "google"},
    )


async def test_gemini_di_google_gpt_di_openai():
    oa, gg = _Gia("openai"), _Gia("google")
    r = _router(openai=oa, google=gg)
    assert (await r.generate([], model="gemini-2.5-flash")).content == "google"
    assert (await r.generate([], model="gpt-4o-mini")).content == "openai"
    assert (await r.generate([], model="model-la")).content == "google"  # theo danh mục
    assert (await r.generate([], model="khong-ro")).content == "openai"  # về mặc định
    assert gg.goi == ["gemini-2.5-flash", "model-la"]


async def test_thieu_khoa_thi_bao_ro_khong_gui_sai_cho():
    r = _router(openai=_Gia("openai"))
    with pytest.raises(ChuaCoKhoaProvider, match="google"):
        await r.generate([], model="gemini-2.5-flash")


def test_danh_muc_co_gemini_va_tier_rieng_cho_google():
    chung = ModelRouter(config_path=str(CATALOG))
    gg = ModelRouter(config_path=str(CATALOG), provider="google")
    assert chung.models["gemini-2.5-flash"]["provider"] == "google"
    assert chung.select_model(tier="cheap") == "gpt-4o-mini"  # hành vi cũ giữ nguyên
    assert gg.select_model(tier="cheap").startswith("gemini")
    assert all(m.startswith("gemini") for m in (gg.select_model(tier=t) for t in ("standard", "reasoning")))
