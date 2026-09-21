"""Composition root — nơi duy nhất ráp các adapter cụ thể vào port.

Không module nào khác được phép tự chọn hiện thực. Mọi tiến trình (API, worker,
CLI) đều gọi `build_container(settings)` để có bộ phụ thuộc của riêng mình.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from adapters.llm.anthropic import AnthropicClient
from adapters.llm.caching import LLMCacheManager
from adapters.llm.chat_port import ChatLlmAdapter
from adapters.llm.mock import MockLLMClient
from adapters.llm.openai import OpenAIClient
from adapters.llm.resilience import FallbackManager
from adapters.llm.router import ModelRouter
from adapters.llm.vllm import VLLMClient
from adapters.persistence.corpus import JsonlPoemCorpus, duong_dan_mac_dinh
from adapters.persistence.memory.blob import LocalBlobRepository
from adapters.persistence.memory.cache import InMemoryCacheRepository
from adapters.persistence.memory.relational import InMemoryRelationalRepository
from adapters.persistence.memory.vector import InMemoryVectorRepository
from adapters.persistence.sql import (
    SqlCacheRepository,
    SqlRateLimiter,
    SqlRelationalRepository,
    SqlVectorRepository,
    dung_dsn_sqlite,
    tao_engine,
)
from adapters.prompts.registry import PromptRegistry
from adapters.rate_limit.memory import InMemoryRateLimiter
from adapters.tools import register_default_tools
from adapters.tools.executor import RegistryToolExecutor
from application.memory.profile import ProfileMemory
from application.memory.session import SessionMemory
from application.poetry.verifier import PoemVerifierDayDu
from application.ports.embedding import EmbeddingPort
from application.ports.generation import GenerationPort
from application.ports.llm import LlmPort
from application.ports.llm_client import LLMClient
from application.ports.poem_corpus import PoemCorpusPort
from application.ports.rate_limit import RateLimitPort
from application.ports.repositories import (
    BlobRepository,
    CacheRepository,
    RelationalRepository,
    VectorRepository,
)
from application.ports.streaming import StreamingPort
from application.ports.tools import ToolPort
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
    # Provider thật, khai đủ ba cổng. CHỈ composition root giữ kiểu gộp này.
    default_llm: LLMClient
    # Ba khung nhìn HẸP trỏ vào cùng một object ở trên. Entrypoint và use case chỉ
    # được nhận khung nhìn hẹp — ADR-0005. Nhờ vậy đổi bộ nhúng sang một hiện thực
    # cục bộ chỉ cần thay `embedder`, không đụng gì tới đường hội thoại.
    embedder: EmbeddingPort
    streamer: StreamingPort
    generator: GenerationPort
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
    # Đường sinh thơ có kiểm định. `chat_llm` là LlmPort (đường đi chính thức),
    # khác `default_llm` vốn là LLMClient cũ — xem adapters/llm/chat_port.py và
    # ADR-0002 về việc hợp nhất hai port (G1b, chưa làm).
    chat_llm: LlmPort
    tools: ToolPort
    rate_limiter: RateLimitPort
    poem_verifier: PoemVerifierDayDu
    poem_corpus: PoemCorpusPort


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


def _dsn_luu_tru(settings: Settings) -> str:
    """DSN của kho SQL. Dùng chung giữa repo, cache và rate-limit."""
    return settings.storage.database_url or dung_dsn_sqlite(
        settings.project_root / settings.storage.sqlite_path
    )


def _build_storage(
    settings: Settings,
) -> tuple[RelationalRepository, VectorRepository, BlobRepository, CacheRepository]:
    """Điểm rẽ nhánh DUY NHẤT của việc chọn nơi lưu dữ liệu.

    `sqlite` thêm ở G9: đóng vấn đề "mất sạch khi restart" bằng thư viện chuẩn,
    kiểm chứng được bằng test thật. `postgres` vẫn là Bước 5 — ADR-0003.

    Kho VECTOR vẫn in-memory ở cả hai nhánh: lưu vector trong SQLite thì mỗi lần
    tìm phải quét toàn bảng và tự tính cosine, tức là chép lại in-memory nhưng
    chậm hơn. Vector cần pgvector hoặc Qdrant thật, không cần một bản nửa vời.
    """
    blob = LocalBlobRepository(base_dir=str(settings.project_root / "data" / "blobs"))

    if settings.storage.kind in ("sqlite", "sql"):
        # Một adapter, hai dialect. `sqlite` là lối tắt đặt DSN cho tệp cục bộ;
        # `sql` nhận DSN bất kỳ, kể cả `postgresql+asyncpg://`.
        dsn = settings.storage.database_url or dung_dsn_sqlite(
            settings.project_root / settings.storage.sqlite_path
        )
        engine = tao_engine(dsn)
        return (
            SqlRelationalRepository(engine),
            # Kho vector cũng bền vững. Xem đính chính trong `sql/vector.py`: quét
            # toàn bảng chậm hơn in-memory, nhưng in-memory MẤT khi restart và
            # KHÔNG dùng chung giữa các tiến trình — hai vấn đề nặng hơn tốc độ.
            # pgvector/Qdrant giải bài toán khác: tìm gần đúng ở quy mô triệu vector.
            SqlVectorRepository(engine),
            blob,
            SqlCacheRepository(engine),
        )

    if settings.storage.kind != "in_memory":
        raise NotImplementedError(
            f"Chưa có adapter lưu trữ '{settings.storage.kind}'. "
            "Xem docs/adr/0003-lo-trinh-adapter-that.md (Bước 5)."
        )
    return (
        InMemoryRelationalRepository(),
        InMemoryVectorRepository(),
        blob,
        InMemoryCacheRepository(),
    )


def build_container(settings: Settings | None = None) -> AppContainer:
    settings = settings or get_settings()

    relational_repo, vector_repo, blob_repo, cache_repo = _build_storage(settings)
    llm = _build_llm(settings)
    token_mgr = TokenManager()
    retriever = HybridRetriever(vector_repo=vector_repo, embedder=llm, rrf_k=settings.rag.rrf_k)

    # Đăng ký tool tường minh, đúng một lần, tại nơi duy nhất biết đủ phụ thuộc.
    register_default_tools(retriever=retriever)

    return AppContainer(
        settings=settings,
        relational_repo=relational_repo,
        vector_repo=vector_repo,
        blob_repo=blob_repo,
        cache_repo=cache_repo,
        default_llm=llm,
        embedder=llm,
        streamer=llm,
        generator=llm,
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
        chat_llm=ChatLlmAdapter(llm, default_model=settings.llm.default_model),
        tools=RegistryToolExecutor(),
        rate_limiter=(
            # Bộ đếm DÙNG CHUNG khi có kho SQL: chạy N worker với bộ đếm trong RAM
            # nghĩa là hạn mức thực tế bị nhân N — lỗ kiểm soát chi phí.
            SqlRateLimiter(tao_engine(_dsn_luu_tru(settings)))
            if settings.storage.kind in ("sqlite", "sql")
            else InMemoryRateLimiter()
        ),
        poem_verifier=PoemVerifierDayDu(),
        poem_corpus=JsonlPoemCorpus(duong_dan_mac_dinh(settings.project_root)),
    )


@lru_cache(maxsize=1)
def get_container() -> AppContainer:
    """Container mặc định của tiến trình. FastAPI ghi đè bằng `app.state` trong lifespan."""
    return build_container(get_settings())
