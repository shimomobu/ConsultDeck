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


class LlmPromptBuilder:
    def build(self, request: LlmGenerationRequest) -> str:
        slide_lines = [
            f"- {slide.slide_id} | title: {slide.title} | role: {slide.role}"
            for slide in request.outline.slides
        ]
        style_lines = [
            f"- {key}: {request.template_context.style_rules[key]}"
            for key in sorted(request.template_context.style_rules)
        ]

        return "\n".join(
            [
                "Generate consulting deck slide content.",
                "",
                "Context:",
                f"Theme: {request.requirement.theme}",
                f"Purpose: {request.requirement.purpose}",
                f"Audience: {request.requirement.audience}",
                f"Tone: {request.requirement.tone}",
                f"Slide count: {request.requirement.slide_count}",
                f"Template: {request.template_context.template_id}",
                f"Doc type: {request.template_context.doc_type}",
                f"Use case: {request.template_context.use_case}",
                f"Template audience: {request.template_context.audience}",
                f"Phase: {request.template_context.phase}",
                "",
                "Style rules:",
                *style_lines,
                "",
                "Slides:",
                *slide_lines,
                "",
                "Return JSON only with this shape:",
                "{",
                '  "slides": [',
                "    {",
                '      "slide_id": "slide-001",',
                '      "message": "one concise message",',
                '      "bullets": ["bullet 1"],',
                '      "notes": "optional speaker note"',
                "    }",
                "  ]",
                "}",
            ]
        )


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
