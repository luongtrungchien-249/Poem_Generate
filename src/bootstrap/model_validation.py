"""Validate configured model locally and verify availability without generation."""

import math

import httpx
import yaml

from bootstrap.settings import Settings


def validate_catalog(settings: Settings) -> dict:
    provider, model = settings.llm.default_provider, settings.llm.default_model
    if provider == "mock":
        return {}
    catalog = yaml.safe_load(settings.models_catalog_path.read_text(encoding="utf-8"))
    entry = catalog.get("models", {}).get(model)
    if not entry or entry.get("provider") != provider:
        raise ValueError(f"Model {model!r} không có trong danh mục của provider {provider!r}.")
    for name in (
        "input_cost_per_million",
        "output_cost_per_million",
        "cached_input_cost_per_million",
    ):
        if (
            not isinstance(entry.get(name), (float, int))
            or isinstance(entry[name], bool)
            or not math.isfinite(entry[name])
            or entry[name] < 0
        ):
            raise ValueError(f"Model {model!r} thiếu giá hợp lệ: {name}.")
    if provider != "vllm" and not entry["output_cost_per_million"]:
        raise ValueError(f"Model {model!r} chưa có giá; không thể đánh giá chi phí.")
    return entry


async def validate_remote_model(settings: Settings) -> None:
    validate_catalog(settings)
    provider = settings.llm.default_provider
    model = settings.llm.default_model
    if provider == "mock":
        return
    key = getattr(settings.secrets, f"{provider}_api_key", None)
    if not key and provider != "vllm":
        if settings.env == "dev" and settings.llm.mock_fallback_on_missing_key:
            return
        raise ValueError(f"Thiếu API key cho {provider}.")
    headers = {}
    if provider == "google":
        url = f"{settings.llm.google_base_url.rstrip('/')}/models/{model}"
        headers = {"x-goog-api-key": key}
    elif provider == "anthropic":
        url = f"https://api.anthropic.com/v1/models/{model}"
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
    else:
        base = settings.llm.vllm_base_url if provider == "vllm" else settings.llm.openai_base_url
        url = f"{base.rstrip('/')}/models" + (f"/{model}" if provider == "openai" else "")
        if key:
            headers = {"Authorization": f"Bearer {key}"}
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.get(url, headers=headers)
        except httpx.HTTPError:
            raise RuntimeError("Không kiểm tra được model: lỗi kết nối provider.") from None
    if response.status_code != 200:
        try:
            reasons = {
                item.get("reason")
                for item in response.json().get("error", {}).get("details", [])
                if isinstance(item, dict)
            }
        except (ValueError, TypeError):
            reasons = set()
        if reasons.intersection({"API_KEY_INVALID", "API_KEY_EXPIRED", "API_KEY_SERVICE_BLOCKED"}):
            raise RuntimeError(
                f"API key của {provider} không hợp lệ hoặc không được phép dùng dịch vụ (HTTP {response.status_code})."
            )
        raise RuntimeError(f"Provider từ chối model {model!r} (HTTP {response.status_code}).")
    body = response.json()
    if provider == "google" and "generateContent" not in body.get("supportedGenerationMethods", []):
        raise ValueError("Model không hỗ trợ generateContent.")
    if provider == "vllm" and model not in {x.get("id") for x in body.get("data", [])}:
        raise ValueError(f"Model {model!r} không được vLLM phục vụ.")
