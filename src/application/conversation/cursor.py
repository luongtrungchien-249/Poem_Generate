"""Opaque cursor for the (updated_at, conversation_id) descending ordering."""

import base64
import json
import math


def encode_cursor(updated_at: float, conversation_id: str) -> str:
    raw = json.dumps([updated_at, conversation_id], separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_cursor(cursor: str) -> tuple[float, str]:
    try:
        value = json.loads(
            base64.b64decode(cursor + "=" * (-len(cursor) % 4), altchars=b"-_", validate=True)
        )
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError
        timestamp, key = value
        if (
            isinstance(timestamp, bool)
            or not isinstance(timestamp, (float, int))
            or not math.isfinite(timestamp)
        ):
            raise ValueError
        if not isinstance(key, str) or not key:
            raise ValueError
        return float(timestamp), key
    except (ValueError, TypeError, UnicodeError) as exc:
        raise ValueError("Cursor không hợp lệ.") from exc
