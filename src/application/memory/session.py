
from application.ports.repositories import RelationalRepository
from contracts.chat import Message
from domain.llm.token import TokenManager


class SessionMemory:
    """Manages short-term conversation memory with sliding token window."""

    def __init__(
        self,
        storage: RelationalRepository,
        max_history_tokens: int = 4000,
        token_mgr: TokenManager | None = None,
    ) -> None:
        self.storage = storage
        self.max_history_tokens = max_history_tokens
        self.token_mgr = token_mgr or TokenManager()

    async def add_message(self, session_id: str, message: Message) -> None:
        await self.storage.save_message(session_id, message)

    async def get_recent_messages(self, session_id: str, max_turns: int = 10) -> list[Message]:
        raw_msgs = await self.storage.get_messages(session_id, limit=max_turns * 2)
        # Apply sliding window truncation
        return self.token_mgr.truncate_context(raw_msgs, max_tokens=self.max_history_tokens)
