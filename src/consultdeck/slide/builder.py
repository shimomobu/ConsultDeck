from uuid import uuid4

from consultdeck.models.outline_spec import OutlineItem, OutlineSpec
from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.models.slide_spec import LayoutType, Slide, SlideSpec
from consultdeck.models.template_spec import TemplateSpec
from consultdeck.slide.content_generator import (
    GeneratedSlideContent,
    LlmGenerationRequest,
    LlmProvider,
    LlmTemplateContext,
)


class SlideBuildError(ValueError):
    """Raised when SlideSpec cannot be built from the provided inputs."""


class SlideBuilder:
    def __init__(self, llm_provider: LlmProvider | None = None) -> None:
        self.llm_provider = llm_provider

    def build(
        self,
        requirement: RequirementSpec,
        outline: OutlineSpec,
        template: TemplateSpec,
        deck_id: str | None = None,
    ) -> SlideSpec:
        if not outline.slides:
            raise SlideBuildError("OutlineSpec.slides must not be empty")

        generated = self._generate_content(requirement, outline, template)
        slides = [
            self._build_slide(
                item,
                requirement=requirement,
                generated=generated.get(item.slide_id),
            )
            for item in outline.slides
        ]

        return SlideSpec(
            deck_id=deck_id or self._deck_id(),
            title=outline.title,
            template_id=template.template_id,
            slides=slides,
        )

    def _build_slide(
        self,
        item: OutlineItem,
        requirement: RequirementSpec,
        generated: GeneratedSlideContent | None = None,
    ) -> Slide:
        if generated:
            try:
                return self._build_generated_slide(item, generated)
            except ValueError:
                pass

        return self._build_deterministic_slide(item, requirement)

    def _build_generated_slide(
        self,
        item: OutlineItem,
        generated: GeneratedSlideContent,
    ) -> Slide:
        layout_type = self._layout_for_role(item.role)
        return Slide(
            slide_id=item.slide_id,
            title=item.title,
            message=generated.message,
            bullets=generated.bullets,
            notes=generated.notes,
            layout_type=layout_type,
        )

    def _build_deterministic_slide(
        self,
        item: OutlineItem,
        requirement: RequirementSpec,
    ) -> Slide:
        layout_type = self._layout_for_role(item.role)
        return Slide(
            slide_id=item.slide_id,
            title=item.title,
            message=f"{requirement.theme}における{item.role}を整理します。",
            bullets=self._bullets_for_role(item.role, layout_type),
            notes=f"Audience: {requirement.audience}",
            layout_type=layout_type,
        )

    def _generate_content(
        self,
        requirement: RequirementSpec,
        outline: OutlineSpec,
        template: TemplateSpec,
    ) -> dict[str, GeneratedSlideContent]:
        if self.llm_provider is None:
            return {}

        try:
            result = self.llm_provider.generate_slide_content(
                LlmGenerationRequest(
                    requirement=requirement,
                    outline=outline,
                    template_context=LlmTemplateContext.from_template(template),
                )
            )
        except Exception:
            return {}

        return result.by_slide_id()

    def _layout_for_role(self, role: str) -> LayoutType:
        normalized = role.strip().casefold()
        if normalized in {"表紙", "タイトル", "title"}:
            return LayoutType.TITLE
        if normalized in {"比較", "対比", "compare", "comparison"}:
            return LayoutType.TWO_COLUMN
        return LayoutType.CONTENT

    def _bullets_for_role(self, role: str, layout_type: LayoutType) -> list[str]:
        if layout_type in {LayoutType.TITLE, LayoutType.BLANK}:
            return []
        return [f"{role}の要点を確認する"]

    def _deck_id(self) -> str:
        return f"deck-{uuid4().hex}"
