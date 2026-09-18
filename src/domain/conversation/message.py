from dataclasses import dataclass
from typing import Literal

from .thread import ThreadScope


@dataclass(frozen=True, slots=True)
class Attachment:
    url: str
    content_type: str
    filename: str | None = None


@dataclass(frozen=True, slots=True)
class ReplyTo:
    message_id: str
    sender_id: str
    text: str


@dataclass(frozen=True, slots=True)
class InboundMessage:
    """Immutable inbound message entering the pipeline with a single invariant trace_id."""
    id: str
    scope: ThreadScope
    sender_id: str
    text: str
    trace_id: str
    reply_to: ReplyTo | None = None
    attachments: tuple[Attachment, ...] = ()
    is_mention: bool = False


@dataclass(frozen=True, slots=True)
class OutboundMessage:
    """Immutable outbound response ready to be dispatched to channels."""
    text: str
    reply_to_id: str | None = None
    attachments: tuple[Attachment, ...] = ()


@dataclass(frozen=True, slots=True)
class StoredMessage:
    """Message stored in conversation history."""
    id: str
    role: Literal["user", "assistant", "system"]
    text: str
    sender_id: str
    created_at_epoch: float
