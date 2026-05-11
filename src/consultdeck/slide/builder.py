from consultdeck.models.outline_spec import OutlineItem, OutlineSpec
from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.models.slide_spec import LayoutType, Slide, SlideSpec
from consultdeck.models.template_spec import TemplateSpec


class SlideBuildError(ValueError):
    """Raised when SlideSpec cannot be built from the provided inputs."""


class SlideBuilder:
    def build(
        self,
        requirement: RequirementSpec,
        outline: OutlineSpec,
        template: TemplateSpec,
    ) -> SlideSpec:
        if not outline.slides:
            raise SlideBuildError("OutlineSpec.slides must not be empty")

        slides = [
            self._build_slide(item, requirement=requirement)
            for item in outline.slides
        ]

        return SlideSpec(
            deck_id=self._deck_id(template),
            title=outline.title,
            template_id=template.template_id,
            slides=slides,
        )

    def _build_slide(
        self,
        item: OutlineItem,
        requirement: RequirementSpec,
    ) -> Slide:
        return Slide(
            slide_id=item.slide_id,
            title=item.title,
            message=f"{requirement.theme}における{item.role}を整理します。",
            bullets=[f"{item.role}の要点を確認する"],
            notes=f"Audience: {requirement.audience}",
            layout_type=self._layout_for_role(item.role),
        )

    def _layout_for_role(self, role: str) -> LayoutType:
        normalized = role.strip().casefold()
        if normalized in {"表紙", "タイトル", "title"}:
            return LayoutType.TITLE
        if normalized in {"比較", "対比", "compare", "comparison"}:
            return LayoutType.TWO_COLUMN
        return LayoutType.CONTENT

    def _deck_id(self, template: TemplateSpec) -> str:
        return f"deck-{template.template_id}"
