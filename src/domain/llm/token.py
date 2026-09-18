from contracts.chat import Message, Role


class TokenManager:
    """Accurate token estimation and sliding window context truncation."""

    def __init__(self, chars_per_token: float = 3.6) -> None:
        self.chars_per_token = chars_per_token

    def count_tokens(self, text: str) -> int:
        if not text:
            return 0
        # Fast character heuristic ratio measured for Vietnamese + English texts
        return max(1, int(len(text) / self.chars_per_token))

    def count_messages_tokens(self, messages: list[Message]) -> int:
        total = 0
        for m in messages:
            total += 4 # Message format overhead
            total += self.count_tokens(m.content)
            if m.name:
                total += self.count_tokens(m.name)
        return total + 2 # Priming tokens

    def truncate_context(
        self,
        messages: list[Message],
        max_tokens: int,
        system_reserve: int = 1000,
    ) -> list[Message]:
        """Truncates conversation history while strictly preserving the System prompt and the most recent User question."""
        if not messages:
            return []

        # Separate system messages from conversational turns
        system_msgs = [m for m in messages if m.role == Role.SYSTEM]
        chat_msgs = [m for m in messages if m.role != Role.SYSTEM]

        system_tokens = self.count_messages_tokens(system_msgs)
        budget_for_chat = max(100, max_tokens - system_tokens)

        retained_chat: list[Message] = []
        accumulated = 0

        # Walk backward from newest message
        for msg in reversed(chat_msgs):
            msg_tokens = self.count_messages_tokens([msg])
            if accumulated + msg_tokens <= budget_for_chat or len(retained_chat) == 0:
                retained_chat.append(msg)
                accumulated += msg_tokens
            else:
                break

        retained_chat.reverse()
        return system_msgs + retained_chat
