from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.models.template_spec import TemplateSpec


class TemplateNotFoundError(LookupError):
    """Raised when a requested template id is not registered."""


class TemplateLoadError(ValueError):
    """Raised when a template YAML file cannot be parsed or validated."""


class TemplateRepository:
    def __init__(self, template_dir: str | Path) -> None:
        self.template_dir = Path(template_dir)

    def get(self, template_id: str) -> TemplateSpec:
        for template in self.list():
            if template.template_id == template_id:
                return template
        raise TemplateNotFoundError(f"Template not found: {template_id}")

    def list(self) -> list[TemplateSpec]:
        if not self.template_dir.exists():
            return []

        templates: list[TemplateSpec] = []
        for path in sorted(self.template_dir.glob("*.yaml")):
            templates.append(self._load_file(path))
        return templates

    def find_matches(self, requirement: RequirementSpec) -> list[TemplateSpec]:
        return [
            template
            for template in self.list()
            if self._matches_requirement(template, requirement)
        ]

    def _load_file(self, path: Path) -> TemplateSpec:
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise TemplateLoadError(f"Invalid template YAML: {path}") from exc

        if not isinstance(raw, dict):
            raise TemplateLoadError(f"Template YAML must be a mapping: {path}")

        try:
            return TemplateSpec.model_validate(raw)
        except ValidationError as exc:
            raise TemplateLoadError(f"Invalid template spec: {path}") from exc

    def _matches_requirement(
        self,
        template: TemplateSpec,
        requirement: RequirementSpec,
    ) -> bool:
        return (
            self._normalize(template.doc_type) == self._normalize(requirement.purpose)
            and self._normalize(template.audience) == self._normalize(requirement.audience)
        )

    def _normalize(self, value: Any) -> str:
        return str(value).strip().casefold()
