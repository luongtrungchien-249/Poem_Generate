from dataclasses import dataclass
from typing import Literal

Platform = Literal["zalo_bot", "zalo_personal", "cli", "web"]


@dataclass(frozen=True, slots=True)
class ThreadScope:
    """Encapsulates platform and thread_id as an atomic immutable scope.
    Never pass platform and thread_id as loose separate parameters.
    """
    platform: Platform
    thread_id: str

    def make_key(self, prefix: str = "") -> str:
        return f"{prefix}:{self.platform}:{self.thread_id}" if prefix else f"{self.platform}:{self.thread_id}"
