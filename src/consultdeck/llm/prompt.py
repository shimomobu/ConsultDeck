from __future__ import annotations

from consultdeck.llm.request import LlmGenerationRequest


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
