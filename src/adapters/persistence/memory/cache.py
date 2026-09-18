import time


class InMemoryCacheRepository:
    """In-memory key-value cache with TTL expiration."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float]] = {}

    async def get(self, key: str) -> str | None:
        item = self._store.get(key)
        if not item:
            return None
        val, expiry = item
        if time.time() > expiry:
            del self._store[key]
            return None
        return val

    async def set(self, key: str, value: str, ttl_seconds: int = 3600) -> None:
        self._store[key] = (value, time.time() + ttl_seconds)

    async def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False
