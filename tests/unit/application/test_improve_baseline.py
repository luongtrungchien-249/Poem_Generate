from dataclasses import dataclass

from evals.baseline import summarize

from domain.llm.token import TokenManager


@dataclass
class PlainMessage:
    role: str
    content: str
    name: str | None = None


def test_token_manager_preserves_original_objects_without_dto():
    system = PlainMessage("system", "instruction")
    question = PlainMessage("user", "latest " * 100)
    assert TokenManager().truncate_context(
        [system, PlainMessage("assistant", "old " * 500), question], 50
    ) == [system, question]


def test_summary_cost_per_pass_and_percentiles():
    rows = [
        {
            "thanh_cong": True,
            "giay": 2,
            "chi_phi_usd": 1,
            "so_luot": 0,
            "luot_reply": 3,
            "so_dong_yc": 4,
        },
        {"thanh_cong": False, "giay": 10, "chi_phi_usd": 3, "luot_reply": 5, "so_dong_yc": 8},
    ]
    summary = summarize(rows)
    assert summary["cost_per_pass"] == 4
    assert summary["pass_rate"] == 0.5
    assert summary["reply_mean"] == 4
    assert summary["p95_seconds"] == 10
    assert summarize([])["cost_per_pass"] is None


def test_price_catalog_is_loaded_for_gemini():
    from adapters.observability.cost import CostCalculator

    calculator = CostCalculator()
    assert calculator.calculate_cost("gemini-3.5-flash-lite", 1_000_000, 1_000_000) == 2.8
