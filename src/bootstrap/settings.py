"""Cấu hình hợp nhất: configs/base.yaml <- configs/<env>.yaml <- biến môi trường.

Đây là nơi DUY NHẤT trong toàn hệ thống được phép đọc `os.environ`.
Mọi tầng khác nhận cấu hình qua tham số, không tự đi tìm.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, TypeVar, cast

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIGS_DIR = PROJECT_ROOT / "configs"

Env = Literal["dev", "staging", "production"]


class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 1


class LLMConfig(BaseModel):
    default_provider: Literal["openai", "anthropic", "vllm", "mock"] = "mock"
    default_model: str = "gpt-4o-mini"
    default_tier: Literal["cheap", "standard", "reasoning"] = "cheap"
    openai_base_url: str = "https://api.openai.com/v1"
    vllm_base_url: str = "http://localhost:8000/v1"
    mock_fallback_on_missing_key: bool = True


class StorageConfig(BaseModel):
    kind: Literal["in_memory", "postgres"] = "in_memory"
    vector_kind: Literal["in_memory", "pgvector", "qdrant"] = "in_memory"
    database_url: str | None = None
    redis_url: str | None = None
    qdrant_url: str | None = None


class RagConfig(BaseModel):
    rrf_k: int = 60
    top_k: int = 4
    rerank_top_n: int = 3
    context_max_tokens: int = 4000


class GuardrailsConfig(BaseModel):
    enabled: bool = True
    policy_file: Path = CONFIGS_DIR / "guardrails.yaml"


class RateLimitConfig(BaseModel):
    capacity: int = 100
    refill_rate: float = 5.0


class Secrets(BaseSettings):
    """Chỉ chứa bí mật, đọc từ môi trường hoặc .env — không bao giờ nằm trong YAML."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")
    qdrant_url: str | None = Field(default=None, alias="QDRANT_URL")


class Settings(BaseModel):
    env: Env = "dev"
    debug: bool = True
    configs_dir: Path = CONFIGS_DIR
    project_root: Path = PROJECT_ROOT
    server: ServerConfig = Field(default_factory=ServerConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    rag: RagConfig = Field(default_factory=RagConfig)
    guardrails: GuardrailsConfig = Field(default_factory=GuardrailsConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    secrets: Secrets = Field(default_factory=Secrets)

    @property
    def models_catalog_path(self) -> Path:
        return self.configs_dir / "models.yaml"


_T = TypeVar("_T", bound=str)


def _kiem_lua_chon(gia_tri: object, hop_le: tuple[_T, ...], ten: str) -> _T:
    """Kiểm một giá trị cấu hình thuộc tập cho phép, ngay lúc nạp.

    Biến môi trường và YAML đều trả chuỗi tự do, trong khi các trường như `env`
    hay `default_provider` chỉ nhận vài giá trị. Không kiểm ở đây thì một giá trị
    sai sẽ trôi vào hệ thống và hỏng ở chỗ khác, xa nơi gây lỗi.
    """
    if gia_tri not in hop_le:
        raise ValueError(f"{ten} = {gia_tri!r} không hợp lệ; chỉ nhận một trong {hop_le}")
    return cast(_T, gia_tri)


ENV_HOP_LE: tuple[Env, ...] = ("dev", "staging", "production")
PROVIDER_HOP_LE: tuple[Literal["openai", "anthropic", "vllm", "mock"], ...] = (
    "openai", "anthropic", "vllm", "mock",
)
TIER_HOP_LE: tuple[Literal["cheap", "standard", "reasoning"], ...] = (
    "cheap", "standard", "reasoning",
)


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_settings(env: str | None = None, configs_dir: Path | None = None) -> Settings:
    """Nạp cấu hình theo thứ tự ưu tiên: base.yaml < <env>.yaml < biến môi trường."""
    cfg_dir = configs_dir or CONFIGS_DIR
    resolved_env = env or os.getenv("ENV", "dev")

    raw = _deep_merge(_read_yaml(cfg_dir / "base.yaml"), _read_yaml(cfg_dir / f"{resolved_env}.yaml"))
    secrets = Secrets()

    app_raw = raw.get("app", {})
    server_raw = raw.get("server", {})
    llm_raw = raw.get("llm", {})
    storage_raw = raw.get("storage", {})
    rag_raw = raw.get("rag", {})
    guard_raw = raw.get("guardrails", {})

    return Settings(
        env=_kiem_lua_chon(
            app_raw.get("env", resolved_env) if app_raw.get("env") != "base" else resolved_env,
            ENV_HOP_LE, "ENV"
        ),
        debug=app_raw.get("debug", resolved_env == "dev"),
        configs_dir=cfg_dir,
        server=ServerConfig(
            host=os.getenv("HOST", server_raw.get("host", "127.0.0.1")),
            port=int(os.getenv("PORT", server_raw.get("port", 8000))),
            workers=int(os.getenv("WORKERS", server_raw.get("workers", 1))),
        ),
        llm=LLMConfig(
            default_provider=_kiem_lua_chon(
                os.getenv("DEFAULT_PROVIDER", llm_raw.get("default_provider", "mock")),
                PROVIDER_HOP_LE, "DEFAULT_PROVIDER"
            ),
            default_model=os.getenv("DEFAULT_MODEL", llm_raw.get("default_model", "gpt-4o-mini")),
            default_tier=_kiem_lua_chon(
                os.getenv("DEFAULT_TIER", llm_raw.get("router", {}).get("default_tier", "cheap")),
                TIER_HOP_LE, "DEFAULT_TIER"
            ),
            openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            vllm_base_url=os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1"),
            mock_fallback_on_missing_key=llm_raw.get("mock_fallback_on_missing_key", True),
        ),
        storage=StorageConfig(
            kind=storage_raw.get("type", "in_memory"),
            vector_kind=storage_raw.get("vector_db", "in_memory"),
            database_url=secrets.database_url,
            redis_url=secrets.redis_url,
            qdrant_url=secrets.qdrant_url,
        ),
        rag=RagConfig(
            rrf_k=rag_raw.get("hybrid", {}).get("rrf_k", 60),
            rerank_top_n=rag_raw.get("rerank", {}).get("top_n", 3),
            context_max_tokens=rag_raw.get("context", {}).get("max_tokens", 4000),
        ),
        guardrails=GuardrailsConfig(
            enabled=_env_bool("ENABLE_GUARDRAILS", guard_raw.get("enabled", True)),
            policy_file=cfg_dir / "guardrails.yaml",
        ),
        rate_limit=RateLimitConfig(
            capacity=int(os.getenv("RATE_LIMIT_CAPACITY", 100)),
            refill_rate=float(os.getenv("RATE_LIMIT_REFILL_RATE", 5.0)),
        ),
        secrets=secrets,
    )


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return load_settings()
