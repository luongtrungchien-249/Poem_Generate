def calculate_faithfulness(answer_text: str, context_text: str) -> float:
    """Estimates hallucination vs grounding: measures word overlap between answer and source context."""
    if not answer_text:
        return 0.0
    if not context_text:
        return 1.0

    answer_words = set(w.lower() for w in answer_text.split() if len(w) > 3)
    context_words = set(w.lower() for w in context_text.split() if len(w) > 3)

    if not answer_words:
        return 1.0

    grounded_words = answer_words.intersection(context_words)
    return round(len(grounded_words) / len(answer_words), 4)


def calculate_answer_relevance(answer_text: str, question_text: str) -> float:
    """Measures relevance of generated answer to question keywords."""
    q_words = set(w.lower() for w in question_text.split() if len(w) > 3)
    a_words = set(w.lower() for w in answer_text.split() if len(w) > 3)

    if not q_words:
        return 1.0

    overlap = q_words.intersection(a_words)
    return round(len(overlap) / len(q_words), 4)
