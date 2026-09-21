import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bootstrap.container import build_container
from bootstrap.settings import get_settings
from entrypoints.api.middleware.auth import AuthMiddleware
from entrypoints.api.middleware.error_handler import ErrorHandlerMiddleware
from entrypoints.api.middleware.rate_limit import RateLimitMiddleware
from entrypoints.api.middleware.request_context import RequestContextMiddleware
from entrypoints.api.routers.chat import router as chat_router
from entrypoints.api.routers.documents import router as documents_router
from entrypoints.api.routers.feedback import router as feedback_router
from entrypoints.api.routers.health import router as health_router
from entrypoints.api.routers.poem import router as poem_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup phase
    logger.info("Initializing AI Platform Production services...")

    # Composition root: mỗi tiến trình dựng bộ phụ thuộc của riêng mình.
    settings = get_settings()
    app.state.settings = settings
    app.state.container = build_container(settings)

    # Warm up prompt registry
    try:
        app.state.container.prompt_reg.get("rag_answer", version="v1")
        logger.info("Prompt registry warmed up successfully.")
    except Exception as e:
        logger.warning(f"Prompt warmup notice: {e}")

    logger.info("AI Platform API ready to accept connections.")
    yield
    # Shutdown phase
    logger.info("Shutting down AI Platform services cleanly...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Platform Production API",
        version="1.0.0",
        description="Production-grade enterprise AI Platform featuring RAG, Agents, Guardrails, and Observability.",
        lifespan=lifespan,
    )

    # Middlewares (order: Outer -> Inner)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RateLimitMiddleware, capacity=100, refill_rate=5.0)
    # AuthMiddleware add SAU RequestContextMiddleware nên chạy TRƯỚC nó: Starlette
    # bọc ngược thứ tự add. Xác thực phải là lớp ngoài cùng của phần nghiệp vụ —
    # request không có khoá thì không đáng tốn một trace_id.
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        AuthMiddleware, khoa_tenant=get_settings().secrets.bang_khoa_tenant()
    )

    # Routers
    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(documents_router)
    app.include_router(feedback_router)
    app.include_router(poem_router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("entrypoints.api.app:app", host="0.0.0.0", port=8000, reload=True)
