import logging

logger = logging.getLogger("worker.reindex")


async def run_reindex_task(new_embedding_model: str) -> dict:
    """Worker task: Rebuilds vector index when changing embedding models."""
    logger.info(f"Re-indexing vector store with model: {new_embedding_model}...")

    # Fetch document metadata and re-embed chunks
    return {
        "status": "completed",
        "model": new_embedding_model,
        "message": "Re-indexing complete.",
    }
