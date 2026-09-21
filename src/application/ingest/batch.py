import math

from application.ports.embedding import EmbeddingPort


def normalize_l2(vector: list[float]) -> list[float]:
    """Applies L2 unit normalization to an embedding vector."""
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0.0:
        return vector
    return [x / norm for x in vector]


class BatchEmbedder:
    """Processes large collections of text chunks in batches."""

    def __init__(self, client: EmbeddingPort, batch_size: int = 32) -> None:
        self.client = client
        self.batch_size = batch_size

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        results: list[list[float]] = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            embeddings = await self.client.embed(batch)
            for vec in embeddings:
                results.append(normalize_l2(vec))
        return results
