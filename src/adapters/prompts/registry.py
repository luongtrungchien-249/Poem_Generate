from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class PromptTemplate(BaseModel):
    name: str
    version: str
    locale: str = "vi"
    metadata: dict[str, Any] = Field(default_factory=dict)
    system: str
    user: str
    variables: list[str] = Field(default_factory=list)

    def render(self, **kwargs: Any) -> tuple[str, str]:
        # Validate all required variables exist
        for var in self.variables:
            if var not in kwargs:
                kwargs[var] = ""
        rendered_system = self.system.format(**kwargs)
        rendered_user = self.user.format(**kwargs)
        return rendered_system, rendered_user


class PromptRegistry:
    """Loads, validates, and caches prompt templates by name, version, and locale."""

    def __init__(self, templates_dir: str | None = None) -> None:
        self.templates_dir = Path(templates_dir) if templates_dir else Path(__file__).parent / "templates"
        self._cache: dict[str, PromptTemplate] = {}

    def _make_key(self, name: str, version: str, locale: str) -> str:
        return f"{name}:{version}:{locale}"

    def get(self, name: str, version: str = "v1", locale: str = "vi") -> PromptTemplate:
        key = self._make_key(name, version, locale)
        if key in self._cache:
            return self._cache[key]

        file_path = self.templates_dir / name / f"{version}.yaml"
        if not file_path.exists():
            # Fallback to default v1 if version not found
            file_path = self.templates_dir / name / "v1.yaml"

        if not file_path.exists():
            raise FileNotFoundError(f"Prompt template '{name}/{version}.yaml' not found in {self.templates_dir}")

        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        template = PromptTemplate(**data)
        self._cache[key] = template
        return template


prompt_registry = PromptRegistry()
