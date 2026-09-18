from dataclasses import dataclass

from application.ports.llm import AssistantMessage, LlmMessage, UserMessage
from domain.conversation.message import StoredMessage

from .budget import enforce_layer_budget
from .builder import wrap_xml_tag


@dataclass(frozen=True, slots=True)
class ContextEnvelope:
    messages: tuple[LlmMessage, ...]
    tokens_used: int
    has_knowledge: bool


def assemble_context_envelope(
    question: str,
    recent_history: tuple[StoredMessage, ...],
    retrieved_knowledge: str | None = None,
    user_facts: str | None = None,
    summary: str | None = None,
) -> ContextEnvelope:
    """Assembles prompt into authentic alternating turns.
    Rule: Never collapse conversation history into a single blob or fake assistant message.
    """
    turn_list: list[LlmMessage] = []
    has_knowledge = False
    tokens_accum = 0

    # 1. Historical turns (excluding any duplicate matching the current question)
    for msg in recent_history:
        if msg.text.strip() == question.strip():
            continue
        if msg.role == "user":
            turn_list.append(UserMessage(content=msg.text))
        elif msg.role == "assistant":
            turn_list.append(AssistantMessage(content=msg.text))

    # 2. Assemble context blocks for the current turn
    blocks = []
    if summary:
        b = enforce_layer_budget(summary, "summary")
        blocks.append(wrap_xml_tag("tom_tat", b.text))

    if user_facts:
        b = enforce_layer_budget(user_facts, "facts")
        blocks.append(wrap_xml_tag("thong_tin_nguoi_dung", b.text))

    if retrieved_knowledge:
        b = enforce_layer_budget(retrieved_knowledge, "knowledge")
        blocks.append(wrap_xml_tag("tai_lieu", b.text))
        has_knowledge = True

    # 3. Final User Question
    q_budget = enforce_layer_budget(question, "question")
    if blocks:
        full_content = "\n\n".join(blocks) + f"\n\n[Câu hỏi]\n{q_budget.text}"
    else:
        full_content = q_budget.text

    turn_list.append(UserMessage(content=full_content))

    return ContextEnvelope(
        messages=tuple(turn_list),
        tokens_used=tokens_accum,
        has_knowledge=has_knowledge,
    )
