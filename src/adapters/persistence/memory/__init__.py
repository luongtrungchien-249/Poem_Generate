"""Hiện thực repository trong RAM — chỉ dùng cho dev và test.

Protocol thuộc về `application/ports/`; ở đây chỉ có hiện thực cụ thể.
"""

from application.ports.repositories import (
    BlobRepository,
    CacheRepository,
    RelationalRepository,
    VectorRepository,
)

from .blob import LocalBlobRepository
from .cache import InMemoryCacheRepository
from .relational import InMemoryRelationalRepository
from .vector import InMemoryVectorRepository

__all__ = [
    "RelationalRepository", "InMemoryRelationalRepository",
    "VectorRepository", "InMemoryVectorRepository",
    "BlobRepository", "LocalBlobRepository",
    "CacheRepository", "InMemoryCacheRepository",
]
