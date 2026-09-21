"""Lưu trữ bền vững trên SQLAlchemy async — một mã, hai dialect.

Chạy nguyên xi trên `sqlite+aiosqlite` (dev, test, một tiến trình) và
`postgresql+asyncpg` (nhiều worker). Xem `engine.py` để biết chỗ DUY NHẤT
trong gói này biết tới dialect.
"""

from .api_key import SqlApiKeyStore
from .engine import dung_dsn_sqlite, la_sqlite, tao_bang, tao_engine
from .rate_limit import SqlRateLimiter
from .relational import SqlCacheRepository, SqlRelationalRepository
from .vector import SqlVectorRepository

__all__ = [
    "SqlRelationalRepository",
    "SqlVectorRepository",
    "SqlCacheRepository",
    "SqlRateLimiter",
    "SqlApiKeyStore",
    "tao_engine",
    "tao_bang",
    "dung_dsn_sqlite",
    "la_sqlite",
]
