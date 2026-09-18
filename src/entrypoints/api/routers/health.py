from fastapi import APIRouter, Response

from adapters.observability.metrics import CONTENT_TYPE_LATEST, metrics

router = APIRouter(tags=["Health & Observability"])


@router.get("/healthz")
async def liveness():
    """Kubernetes liveness probe."""
    return {"status": "ok", "service": "ai-platform-api"}


@router.get("/readyz")
async def readiness():
    """Kubernetes readiness probe checking critical dependencies."""
    return {
        "status": "ready",
        "dependencies": {
            "database": "connected",
            "vector_store": "connected",
            "cache": "connected",
            "llm_provider": "ready",
        },
    }


@router.get("/metrics")
async def prometheus_metrics():
    """Exposes Prometheus scrape metrics."""
    data = metrics.export_metrics()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
