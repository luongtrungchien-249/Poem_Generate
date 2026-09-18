"""Composition root — nơi duy nhất ráp các adapter cụ thể vào port.

Không module nào khác được phép tự chọn hiện thực. Mọi tiến trình (API, worker,
CLI) đều gọi `build_container(settings)` để có bộ phụ thuộc của riêng mình.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from adapters.llm.anthropic import AnthropicClient
from adapters.llm.caching import LLMCacheManager
from adapters.llm.mock import MockLLMClient
from adapters.llm.openai import OpenAIClient
from adapters.llm.resilience import FallbackManager
from adapters.llm.router import ModelRouter
from adapters.llm.vllm import VLLMClient
from adapters.persistence.memory.blob import LocalBlobRepository
from adapters.persistence.memory.cache import InMemoryCacheRepository
from adapters.persistence.memory.relational import InMemoryRelationalRepository
from adapters.persistence.memory.vector import InMemoryVectorRepository
from adapters.prompts.registry import PromptRegistry
from adapters.tools import register_default_tools
from application.agent.graph import AgentGraph
from application.memory.profile import ProfileMemory
from application.memory.session import SessionMemory
from application.ports.llm_client import LLMClient
from application.ports.repositories import (
    BlobRepository,
    CacheRepository,
    RelationalRepository,
    VectorRepository,
)
from application.rag.context_builder import ContextAssembler
from application.rag.reranker import FastHeuristicReranker
from application.rag.retriever import HybridRetriever
from bootstrap.settings import Settings, get_settings
from domain.llm.token import TokenManager


@dataclass(slots=True)
class AppContainer:
    """Bộ phụ thuộc đã ráp xong của một tiến trình."""

    settings: Settings
    relational_repo: RelationalRepository
    vector_repo: VectorRepository
    blob_repo: BlobRepository
    cache_repo: CacheRepository
    default_llm: LLMClient
    default_model: str
    router: ModelRouter
    fallback_mgr: FallbackManager
    cache_mgr: LLMCacheManager
    token_mgr: TokenManager
    prompt_reg: PromptRegistry
    retriever: HybridRetriever
    reranker: FastHeuristicReranker
    context_assembler: ContextAssembler
    session_memory: SessionMemory
    profile_memory: ProfileMemory
    agent_graph: AgentGraph


def _build_llm(settings: Settings) -> LLMClient:
    """Chọn provider theo cấu hình; thiếu khoá thì lùi về mock nếu dev cho phép."""
    provider = settings.llm.default_provider
    secrets = settings.secrets

    if provider == "openai":
        if secrets.openai_api_key:
            return OpenAIClient(api_key=secrets.openai_api_key, base_url=settings.llm.openai_base_url)
        if not settings.llm.mock_fallback_on_missing_key:
            raise RuntimeError("Thiếu OPENAI_API_KEY và cấu hình không cho phép lùi về mock.")
        return MockLLMClient()

    if provider == "anthropic":
        if secrets.anthropic_api_key:
            return AnthropicClient(api_key=secrets.anthropic_api_key)
        if not settings.llm.mock_fallback_on_missing_key:
            raise RuntimeError("Thiếu ANTHROPIC_API_KEY và cấu hình không cho phép lùi về mock.")
        return MockLLMClient()

    if provider == "vllm":
        return VLLMClient(base_url=settings.llm.vllm_base_url)

    return MockLLMClient()


def _build_storage(
    settings: Settings,
) -> tuple[RelationalRepository, VectorRepository, BlobRepository, CacheRepository]:
    """Bước 5 của lộ trình sẽ thêm nhánh postgres/pgvector/redis tại đây."""
    if settings.storage.kind != "in_memory":
        raise NotImplementedError(
            f"Chưa có adapter lưu trữ '{settings.storage.kind}'. "
            "Xem docs/adr/0003-lo-trinh-adapter-that.md (Bước 5)."
        )
    return (
        InMemoryRelationalRepository(),
        InMemoryVectorRepository(),
        LocalBlobRepository(base_dir=str(settings.project_root / "data" / "blobs")),
        InMemoryCacheRepository(),
    )


def build_container(settings: Settings | None = None) -> AppContainer:
    settings = settings or get_settings()

    relational_repo, vector_repo, blob_repo, cache_repo = _build_storage(settings)
    llm = _build_llm(settings)
    token_mgr = TokenManager()
    retriever = HybridRetriever(vector_repo=vector_repo, llm_client=llm, rrf_k=settings.rag.rrf_k)

    # Đăng ký tool tường minh, đúng một lần, tại nơi duy nhất biết đủ phụ thuộc.
    register_default_tools(retriever=retriever)

    return AppContainer(
        settings=settings,
        relational_repo=relational_repo,
        vector_repo=vector_repo,
        blob_repo=blob_repo,
        cache_repo=cache_repo,
        default_llm=llm,
        default_model=settings.llm.default_model,
        router=ModelRouter(config_path=str(settings.models_catalog_path)),
        fallback_mgr=FallbackManager(),
        cache_mgr=LLMCacheManager(cache_repo=cache_repo),
        token_mgr=token_mgr,
        prompt_reg=PromptRegistry(),
        retriever=retriever,
        reranker=FastHeuristicReranker(),
        context_assembler=ContextAssembler(token_mgr=token_mgr),
        session_memory=SessionMemory(storage=relational_repo, token_mgr=token_mgr),
        profile_memory=ProfileMemory(),
        agent_graph=AgentGraph(llm_client=llm),
    )


@lru_cache(maxsize=1)
def get_container() -> AppContainer:
    """Container mặc định của tiến trình. FastAPI ghi đè bằng `app.state` trong lifespan."""
    return build_container(get_settings())
