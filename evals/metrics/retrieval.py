def calculate_recall_at_k(retrieved_chunk_ids: list[str], expected_chunk_ids: list[str], k: int = 5) -> float:
    """Calculates Recall@k."""
    if not expected_chunk_ids:
        return 1.0
    top_k = retrieved_chunk_ids[:k]
    hits = sum(1 for cid in expected_chunk_ids if cid in top_k)
    return round(hits / len(expected_chunk_ids), 4)


def calculate_mrr(retrieved_chunk_ids: list[str], expected_chunk_ids: list[str]) -> float:
    """Calculates Mean Reciprocal Rank (MRR)."""
    if not expected_chunk_ids:
        return 1.0
    for rank, cid in enumerate(retrieved_chunk_ids, start=1):
        if cid in expected_chunk_ids:
            return round(1.0 / rank, 4)
    return 0.0


def calculate_precision_at_k(retrieved_chunk_ids: list[str], expected_chunk_ids: list[str], k: int = 5) -> float:
    """Calculates Precision@k."""
    if not retrieved_chunk_ids or k <= 0:
        return 0.0
    top_k = retrieved_chunk_ids[:k]
    hits = sum(1 for cid in top_k if cid in expected_chunk_ids)
    return round(hits / len(top_k), 4)
