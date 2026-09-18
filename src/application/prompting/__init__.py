"""Prompt construction: 3 lifecycle layers, budget circuit breakers, tag sanitization."""

from .budget import CHARS_PER_TOKEN, TOKEN_BUDGET, BudgetLayer, enforce_layer_budget
from .builder import sanitize_tag_lookalikes, wrap_xml_tag
from .context import ContextEnvelope, assemble_context_envelope
from .instructions import RAG_INSTRUCTION, REACT_INSTRUCTION
from .system import SYSTEM_PROMPT_V1

__all__ = [
    "SYSTEM_PROMPT_V1",
    "RAG_INSTRUCTION",
    "REACT_INSTRUCTION",
    "sanitize_tag_lookalikes",
    "wrap_xml_tag",
    "BudgetLayer",
    "enforce_layer_budget",
    "CHARS_PER_TOKEN",
    "TOKEN_BUDGET",
    "ContextEnvelope",
    "assemble_context_envelope",
]
