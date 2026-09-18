"""Hội thoại: phạm vi luồng (ThreadScope) và các loại tin nhắn bất biến."""

from .message import Attachment, InboundMessage, OutboundMessage, ReplyTo, StoredMessage
from .thread import Platform, ThreadScope

__all__ = [
    "Platform", "ThreadScope",
    "Attachment", "ReplyTo", "InboundMessage", "OutboundMessage", "StoredMessage",
]
