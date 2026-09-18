

def calculate_tool_selection_accuracy(selected_tools: list[str], expected_tools: list[str]) -> float:
    """Measures precision of tool calls made by agent."""
    if not expected_tools:
        return 1.0 if not selected_tools else 0.5
    if not selected_tools:
        return 0.0

    correct = sum(1 for t in selected_tools if t in expected_tools)
    return round(correct / max(len(selected_tools), len(expected_tools)), 4)


def calculate_step_efficiency(steps_taken: int, optimal_steps: int) -> float:
    """Evaluates whether agent resolved query without wasteful trajectory loops."""
    if steps_taken <= 0:
        return 0.0
    if steps_taken <= optimal_steps:
        return 1.0
    return round(optimal_steps / steps_taken, 4)
