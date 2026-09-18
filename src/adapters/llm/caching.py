import hashlib
import json
from typing import Any

from application.ports.llm_client import LLMResponse
from application.ports.repositories import CacheRepository
from contracts.chat import Message
from domain.knowledge.similarity import cosine_similarity as _cosine_similarity


class LLMCacheManager:
    """Combines exact hash caching and semantic embedding similarity caching."""

    def __init__(
        self,
        cache_repo: CacheRepository,
        semantic_threshold: float = 0.92,
    ) -> None:
        # Hiện thực cache do composition root truyền vào: adapter không tự chọn adapter khác.
        self.cache_repo = cache_repo
        self.semantic_threshold = semantic_threshold
        # In-memory storage for semantic cache index: (query_text, embedding, response_json)
        self._semantic_index: list[tuple[str, list[float], dict[str, Any]]] = []

    def _hash_messages(self, messages: list[Message], model: str, temperature: float) -> str:
        serialized = json.dumps(
            [{"r": m.role.value, "c": m.content} for m in messages],
            sort_keys=True,
        )
        key = f"exact:{model}:{temperature}:{serialized}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    async def get_exact(self, messages: list[Message], model: str, temperature: float) -> LLMResponse | None:
        cache_key = self._hash_messages(messages, model, temperature)
        raw = await self.cache_repo.get(cache_key)
        if raw:
            data = json.loads(raw)
            return LLMResponse(**data)
        return None

    async def set_exact(self, messages: list[Message], model: str, temperature: float, response: LLMResponse, ttl: int = 3600) -> None:
        cache_key = self._hash_messages(messages, model, temperature)
        await self.cache_repo.set(cache_key, response.model_dump_json(), ttl_seconds=ttl)

    async def get_semantic(self, query_text: str, query_embedding: list[float]) -> LLMResponse | None:
        if not query_embedding:
            return None
        for _stored_query, stored_embedding, resp_data in self._semantic_index:
            sim = _cosine_similarity(query_embedding, stored_embedding)
            if sim >= self.semantic_threshold:
                return LLMResponse(**resp_data)
        return None

    async def set_semantic(self, query_text: str, query_embedding: list[float], response: LLMResponse) -> None:
        if query_embedding:
            self._semantic_index.append((query_text, query_embedding, response.model_dump()))
