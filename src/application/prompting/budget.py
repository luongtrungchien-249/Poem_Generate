from typing import Literal, NamedTuple, TypeAlias

BudgetLayer: TypeAlias = Literal["system", "knowledge", "facts", "summary", "recent", "question", "tool"]

# Measured ratio: 3.6 chars per token for Vietnamese + English mix
CHARS_PER_TOKEN = 3.6

TOKEN_BUDGET: dict[BudgetLayer, int] = {
    "system": 1000,
    "knowledge": 4000,
    "facts": 1000,
    "summary": 1000,
    "recent": 3000,
    "question": 1000,
    "tool": 2000,
}


class BudgetCheck(NamedTuple):
    text: str
    tokens: int
    truncated_tokens: int


def enforce_layer_budget(text: str, layer: BudgetLayer) -> BudgetCheck:
    budget = TOKEN_BUDGET.get(layer, 2000)
    estimated_tokens = int(len(text) / CHARS_PER_TOKEN)

    if estimated_tokens <= budget:
        return BudgetCheck(text=text, tokens=estimated_tokens, truncated_tokens=0)

    # Exceeded budget: slice text to strictly fit within token budget
    max_chars = int(budget * CHARS_PER_TOKEN)
    truncated_text = text[:max_chars]
    truncated_tokens = estimated_tokens - budget

    return BudgetCheck(text=truncated_text, tokens=budget, truncated_tokens=truncated_tokens)
