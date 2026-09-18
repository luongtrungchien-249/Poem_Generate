from typing import Literal

GroupPolicy = Literal["allowlist", "open", "disabled"]
DmPolicy = Literal["pairing", "allowlist", "open", "disabled"]


def is_group_allowed(policy: GroupPolicy, thread_id: str, allowlist: frozenset[str]) -> bool:
    """Pure predicate for group access verification."""
    if policy == "disabled":
        return False
    if policy == "open":
        return True
    return thread_id in allowlist


def is_dm_allowed(policy: DmPolicy, sender_id: str, allowlist: frozenset[str]) -> bool:
    """Pure predicate for DM access verification."""
    if policy == "disabled":
        return False
    if policy == "open":
        return True
    return sender_id in allowlist
