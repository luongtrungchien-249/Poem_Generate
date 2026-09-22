from fastapi import APIRouter, Response

from adapters.observability.metrics import CONTENT_TYPE_LATEST, metrics

router = APIRouter(tags=["Health & Observability"])


@router.get("/")
async def goc():
    """Chỉ đường, thay vì một `404 Not Found` trống rỗng.

    Backend này chỉ phục vụ API, không phục vụ trang web — giao diện nằm ở một
    tiến trình khác (Next.js, cổng 3000). Nhưng người mở `http://127.0.0.1:8000`
    trong trình duyệt thì thấy `{"detail":"Not Found"}` và không có cách nào biết
    đó là hành vi ĐÚNG hay là máy chủ hỏng.

    Một dòng chỉ đường ở đây rẻ hơn nhiều so với thời gian người ta mất để tự đoán.
    """
    return {
        "service": "ai-platform-api",
        "thong_bao": "Đây là API, không phải giao diện web.",
        "giao_dien_web": "http://localhost:3000",
        "tai_lieu_api": "/docs",
        "kiem_tra_song": "/healthz",
    }


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
