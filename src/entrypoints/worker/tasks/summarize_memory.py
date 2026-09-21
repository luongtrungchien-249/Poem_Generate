import logging

from bootstrap.container import get_container
from contracts.chat import Role
from domain.conversation.tenant import TenantScope

logger = logging.getLogger("worker.summarize_memory")


async def run_summarize_memory_task(
    session_id: str, user_id: str, tenant_id: str = "default"
) -> None:
    """Worker task: Compresses short-term messages and extracts persistent user facts."""
    container = get_container()
    logger.info(f"Summarizing memory for session '{session_id}', user '{user_id}'...")
    msgs = await container.session_memory.get_recent_messages(
        TenantScope(tenant_id=tenant_id), session_id, max_turns=20
    )

    if not msgs:
        return

    # Extract user profile traits or preferences
    for m in msgs:
        if m.role == Role.USER:
            if "tôi tên là" in m.content.lower():
                name = m.content.split("tôi tên là")[-1].strip().split()[0]
                await container.profile_memory.save_fact(user_id, "name", name)
            elif "ngôn ngữ yêu thích là" in m.content.lower():
                lang = m.content.split("ngôn ngữ yêu thích là")[-1].strip().split()[0]
                await container.profile_memory.save_fact(user_id, "preferred_language", lang)

    logger.info(f"User profile facts updated for {user_id}.")
