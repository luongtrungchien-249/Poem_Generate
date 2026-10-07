import httpx
import pytest

from bootstrap.model_validation import validate_catalog, validate_remote_model
from bootstrap.settings import LLMConfig, Secrets, Settings


def test_unknown_model_and_wrong_provider_fail_early():
    with pytest.raises(ValueError):
        validate_catalog(
            Settings(llm=LLMConfig(default_provider="google", default_model="not-a-model"))
        )
    with pytest.raises(ValueError):
        validate_catalog(
            Settings(llm=LLMConfig(default_provider="google", default_model="gpt-4o-mini"))
        )


async def test_invalid_key_is_classified_without_logging_provider_body(monkeypatch):
    class Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, *args, **kwargs):
            return httpx.Response(
                400,
                json={
                    "error": {"message": "secret-value", "details": [{"reason": "API_KEY_INVALID"}]}
                },
            )

    monkeypatch.setattr(httpx, "AsyncClient", Client)
    settings = Settings(
        llm=LLMConfig(default_provider="google", default_model="gemini-3.5-flash-lite"),
        secrets=Secrets(_env_file=None, GOOGLE_API_KEY="test-key"),
    )
    with pytest.raises(RuntimeError) as error:
        await validate_remote_model(settings)
    assert "API key" in str(error.value)
    assert "secret-value" not in str(error.value)


async def test_production_missing_key_never_silently_falls_back_to_mock():
    settings = Settings(
        env="production",
        secrets=Secrets(_env_file=None, GOOGLE_API_KEY=""),
        llm=LLMConfig(default_provider="google", default_model="gemini-3.5-flash-lite"),
    )
    with pytest.raises(ValueError, match="Thiếu API key"):
        await validate_remote_model(settings)


async def test_dev_missing_key_can_keep_explicit_mock_fallback():
    settings = Settings(
        secrets=Secrets(_env_file=None, GOOGLE_API_KEY=""),
        llm=LLMConfig(default_provider="google", default_model="gemini-3.5-flash-lite"),
    )
    await validate_remote_model(settings)
