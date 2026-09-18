
from contracts.chat import Message
from contracts.chunk import Document
from contracts.feedback import FeedbackRecord


class InMemoryRelationalRepository:
    """In-memory implementation for testing and development."""

    def __init__(self) -> None:
        self._sessions: dict[str, list[Message]] = {}
        self._documents: dict[str, Document] = {}
        self._feedbacks: list[FeedbackRecord] = []

    async def save_message(self, session_id: str, message: Message) -> None:
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append(message)

    async def get_messages(self, session_id: str, limit: int = 50) -> list[Message]:
        msgs = self._sessions.get(session_id, [])
        return msgs[-limit:]

    async def save_document_meta(self, doc: Document) -> None:
        self._documents[doc.id] = doc

    async def get_document_meta(self, doc_id: str) -> Document | None:
        return self._documents.get(doc_id)

    async def save_feedback(self, feedback: FeedbackRecord) -> None:
        self._feedbacks.append(feedback)

    async def get_feedbacks(self, limit: int = 100) -> list[FeedbackRecord]:
        return self._feedbacks[-limit:]
