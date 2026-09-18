from typing import Protocol

from domain.conversation.message import OutboundMessage
from domain.conversation.thread import ThreadScope


class ChannelPort(Protocol):
    """Port for platform I/O delivery (Zalo, Web, Slack, CLI)."""

    @property
    def max_message_chars(self) -> int: ...

    async def typing(self, scope: ThreadScope) -> None: ...

    async def send(self, scope: ThreadScope, msg: OutboundMessage) -> None: ...
