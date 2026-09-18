from datetime import datetime
from typing import NamedTuple


class UserFact(NamedTuple):
    id: str
    user_id: str
    key: str # e.g. "preferred_language", "role", "interests"
    value: str
    confidence: float
    updated_at: datetime


class ProfileMemory:
    """Manages long-term user profile facts and preferences."""

    def __init__(self) -> None:
        self._facts: dict[str, dict[str, UserFact]] = {}

    async def save_fact(self, user_id: str, key: str, value: str, confidence: float = 1.0) -> None:
        if user_id not in self._facts:
            self._facts[user_id] = {}
        fact_id = f"fact-{len(self._facts[user_id]) + 1}"
        fact = UserFact(
            id=fact_id,
            user_id=user_id,
            key=key,
            value=value,
            confidence=confidence,
            updated_at=datetime.utcnow(),
        )
        self._facts[user_id][key] = fact

    async def get_facts(self, user_id: str) -> list[UserFact]:
        return list(self._facts.get(user_id, {}).values())

    async def render_profile_summary(self, user_id: str) -> str:
        facts = await self.get_facts(user_id)
        if not facts:
            return ""
        lines = [f"- {f.key}: {f.value}" for f in facts]
        return "\n".join(lines)
