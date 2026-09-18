from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest


class MetricsRegistry:
    """Manages application-wide Prometheus metrics for AI workloads."""

    def __init__(self) -> None:
        # Request counts
        self.request_count = Counter(
            "ai_platform_requests_total",
            "Total AI requests processed",
            ["endpoint", "tenant_id", "status"],
        )
        
        # Latency histograms
        self.request_latency = Histogram(
            "ai_platform_request_duration_seconds",
            "Request processing duration in seconds",
            ["endpoint", "model"],
            buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
        )
        self.time_to_first_token = Histogram(
            "ai_platform_time_to_first_token_seconds",
            "Time to first token (TTFT) for streaming responses",
            ["model"],
            buckets=(0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0),
        )

        # Token usage
        self.token_count = Counter(
            "ai_platform_tokens_total",
            "Total tokens consumed",
            ["model", "token_type"], # prompt, completion, cached
        )

        # Fallback & Circuit breaker
        self.fallback_events = Counter(
            "ai_platform_fallback_events_total",
            "Number of fallback triggers",
            ["primary_model", "fallback_model", "reason"],
        )

        # Active requests gauge
        self.active_requests = Gauge(
            "ai_platform_active_requests",
            "Number of requests currently in flight",
        )

    def record_request(self, endpoint: str, tenant_id: str, status: str, duration_sec: float, model: str = "unknown") -> None:
        self.request_count.labels(endpoint=endpoint, tenant_id=tenant_id, status=status).inc()
        self.request_latency.labels(endpoint=endpoint, model=model).observe(duration_sec)

    def record_tokens(self, model: str, prompt_tokens: int, completion_tokens: int, cached_tokens: int = 0) -> None:
        self.token_count.labels(model=model, token_type="prompt").inc(prompt_tokens)
        self.token_count.labels(model=model, token_type="completion").inc(completion_tokens)
        if cached_tokens > 0:
            self.token_count.labels(model=model, token_type="cached").inc(cached_tokens)

    def export_metrics(self) -> bytes:
        return generate_latest()


metrics = MetricsRegistry()


__all__ = ["MetricsRegistry", "metrics", "CONTENT_TYPE_LATEST"]
