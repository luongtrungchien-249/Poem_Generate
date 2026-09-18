from pathlib import Path
from typing import Any, Literal

import yaml


class ModelRouter:
    """Intelligently routes requests to the optimal model based on tier, query complexity, and budget."""

    def __init__(self, config_path: str | None = None) -> None:
        self.tiers: dict[str, dict[str, Any]] = {}
        self.models: dict[str, dict[str, Any]] = {}
        self._load_config(config_path)

    def _load_config(self, config_path: str | None) -> None:
        path = Path(config_path) if config_path else Path(__file__).parents[3] / "configs" / "models.yaml"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self.models = data.get("models", {})
                self.tiers = data.get("tiers", {})
        else:
            self.tiers = {
                "cheap": {"primary": "gpt-4o-mini", "fallback": ["mock-gpt"]},
                "standard": {"primary": "gpt-4o", "fallback": ["mock-gpt"]},
                "reasoning": {"primary": "o1-preview", "fallback": ["gpt-4o", "mock-gpt"]},
            }

    def select_model(
        self,
        explicit_model: str | None = None,
        tier: Literal["cheap", "standard", "reasoning"] | None = "standard",
        query_text: str | None = None,
    ) -> str:
        # If user explicitly requested an allowed model, use it
        if explicit_model:
            return explicit_model

        # Heuristic: If query requires complex reasoning (e.g. math, deep code, multistep), promote tier
        detected_tier = tier or "standard"
        if query_text:
            lowered = query_text.lower()
            complex_keywords = ["chứng minh", "phân tích sâu", "tối ưu thuật toán", "step by step", "complex architecture"]
            if any(k in lowered for k in complex_keywords) and detected_tier == "cheap":
                detected_tier = "standard"

        tier_config = self.tiers.get(detected_tier, self.tiers.get("standard", {}))
        return tier_config.get("primary", "gpt-4o")

    def get_fallback_chain(self, primary_model: str) -> list[str]:
        # Find which tier this model belongs to
        for tier_info in self.tiers.values():
            if tier_info.get("primary") == primary_model:
                return tier_info.get("fallback", ["mock-gpt"])
        return ["mock-gpt"]
