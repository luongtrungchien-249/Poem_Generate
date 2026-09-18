from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    """Immutable retrieved knowledge chunk value object."""
    chunk_id: str
    doc_id: str
    text: str
    score: float
    metadata: tuple[tuple[str, Any], ...] = ()

    def get_meta(self, key: str, default: Any = None) -> Any:
        for k, v in self.metadata:
            if k == key:
                return v
        return default
