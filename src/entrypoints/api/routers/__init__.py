"""API routers module."""

from .chat import router as chat_router
from .documents import router as documents_router
from .feedback import router as feedback_router
from .health import router as health_router

__all__ = ["chat_router", "documents_router", "feedback_router", "health_router"]
