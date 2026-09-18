import asyncio
import random
import time
from collections.abc import Callable
from typing import Any

from adapters.observability.metrics import metrics


class CircuitBreakerOpenException(Exception):
    pass


class CircuitBreaker:
    """Circuit breaker pattern for protecting against cascading upstream failures."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout_sec: float = 60.0) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state: str = "CLOSED" # CLOSED, OPEN, HALF_OPEN

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def allow_request(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if self.last_failure_time and (time.time() - self.last_failure_time > self.recovery_timeout_sec):
                self.state = "HALF_OPEN"
                return True
            return False
        if self.state == "HALF_OPEN":
            return True
        return True


class FallbackManager:
    """Executes LLM operations with retry, jitter, circuit breaker, and model fallbacks."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_backoff: float = 0.5,
        backoff_factor: float = 2.0,
    ) -> None:
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.backoff_factor = backoff_factor
        self.breakers: dict[str, CircuitBreaker] = {}

    def get_breaker(self, model: str) -> CircuitBreaker:
        if model not in self.breakers:
            self.breakers[model] = CircuitBreaker()
        return self.breakers[model]

    async def execute_with_fallback(
        self,
        primary_model: str,
        fallback_models: list[str],
        func: Callable[[str], Any],
    ) -> Any:
        models_to_try = [primary_model] + [m for m in fallback_models if m != primary_model]
        last_exception: Exception | None = None

        for model in models_to_try:
            breaker = self.get_breaker(model)
            if not breaker.allow_request():
                metrics.fallback_events.labels(
                    primary_model=primary_model,
                    fallback_model=model,
                    reason="circuit_breaker_open",
                ).inc()
                continue

            # Attempt with retries
            for attempt in range(self.max_retries):
                try:
                    result = await func(model)
                    breaker.record_success()
                    return result
                except Exception as exc:
                    breaker.record_failure()
                    last_exception = exc
                    if attempt < self.max_retries - 1:
                        # Exponential backoff + jitter
                        sleep_time = (self.initial_backoff * (self.backoff_factor ** attempt)) + random.uniform(0, 0.1)
                        await asyncio.sleep(sleep_time)

            metrics.fallback_events.labels(
                primary_model=primary_model,
                fallback_model=model,
                reason="retry_exhausted",
            ).inc()

        if last_exception:
            raise last_exception
        raise RuntimeError("All models in fallback chain failed or circuit breakers are open.")
