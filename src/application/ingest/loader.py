import uuid
from typing import Any

from contracts.chunk import Document


class DocumentLoader:
    """Parses raw text/markdown/html files into standardized Document objects."""

    @staticmethod
    def from_text(
        text: str,
        title: str,
        tenant_id: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> Document:
        doc_id = f"doc_{uuid.uuid4().hex[:10]}"
        return Document(
            id=doc_id,
            tenant_id=tenant_id,
            title=title,
            content=text.strip(),
            mime_type="text/plain",
            metadata=metadata or {},
        )
