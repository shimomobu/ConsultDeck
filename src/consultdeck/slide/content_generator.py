from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from consultdeck.models.outline_spec import OutlineSpec
from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.models.template_spec import TemplateSpec


@dataclass(frozen=True)
class LlmTemplateContext:
    template_id: str
    doc_type: str
    use_case: str
    audience: str
    phase: str
    style_rules: dict[str, Any]

    @classmethod
    def from_template(cls, template: TemplateSpec) -> "LlmTemplateContext":
        return cls(
            template_id=template.template_id,
            doc_type=template.doc_type,
            use_case=template.use_case,
            audience=template.audience,
            phase=template.phase,
            style_rules=dict(template.style_rules),
        )


@dataclass(frozen=True)
class LlmGenerationRequest:
    requirement: RequirementSpec
    outline: OutlineSpec
    template_context: LlmTemplateContext


@dataclass(frozen=True)
class GeneratedSlideContent:
    slide_id: str
    message: str
    bullets: list[str] = field(default_factory=list)
    notes: str | None = None


@dataclass(frozen=True)
class LlmGenerationResult:
    slides: list[GeneratedSlideContent]

    def by_slide_id(self) -> dict[str, GeneratedSlideContent]:
        return {slide.slide_id: slide for slide in self.slides}


class LlmProvider(Protocol):
    def generate_slide_content(
        self,
        request: LlmGenerationRequest,
    ) -> LlmGenerationResult:
        """Generate slide body content for a structured request."""


class FakeLlmProvider:
    def __init__(self, result: LlmGenerationResult) -> None:
        self.result = result

    def generate_slide_content(
        self,
        request: LlmGenerationRequest,
    ) -> LlmGenerationResult:
        return self.result
