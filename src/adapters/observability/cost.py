from pathlib import Path

import yaml


class CostCalculator:
    """Calculates dollar costs for model token consumption."""

    def __init__(self, config_path: str | None = None) -> None:
        self.pricing: dict[str, dict[str, float]] = {}
        self._load_pricing(config_path)

    def _load_pricing(self, config_path: str | None) -> None:
        path = Path(config_path) if config_path else Path(__file__).parents[2] / "configs" / "models.yaml"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                models = data.get("models", {})
                for model_name, info in models.items():
                    self.pricing[model_name] = {
                        "input": info.get("input_cost_per_million", 0.0),
                        "output": info.get("output_cost_per_million", 0.0),
                        "cached": info.get("cached_input_cost_per_million", 0.0),
                    }
        else:
            # Fallback default pricing
            self.pricing = {
                "gpt-4o-mini": {"input": 0.15, "output": 0.60, "cached": 0.075},
                "gpt-4o": {"input": 5.00, "output": 15.00, "cached": 2.50},
                "claude-3-5-sonnet": {"input": 3.00, "output": 15.00, "cached": 0.30},
                "mock-gpt": {"input": 0.0, "output": 0.0, "cached": 0.0},
            }

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int, cached_tokens: int = 0) -> float:
        # Match prefix or exact model name
        rates = self.pricing.get(model)
        if not rates:
            for k, v in self.pricing.items():
                if k in model:
                    rates = v
                    break
        if not rates:
            rates = {"input": 0.0, "output": 0.0, "cached": 0.0}

        effective_prompt_tokens = max(0, prompt_tokens - cached_tokens)
        cost_input = (effective_prompt_tokens / 1_000_000.0) * rates["input"]
        cost_cached = (cached_tokens / 1_000_000.0) * rates["cached"]
        cost_output = (completion_tokens / 1_000_000.0) * rates["output"]

        return round(cost_input + cost_cached + cost_output, 6)


cost_calculator = CostCalculator()
