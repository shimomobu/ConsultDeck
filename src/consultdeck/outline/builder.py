from consultdeck.models.outline_spec import OutlineItem, OutlineSpec
from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.models.template_spec import TemplateSpec


class OutlineBuildError(ValueError):
    """Raised when an outline cannot be built from the provided inputs."""


class OutlineBuilder:
    def build(
        self,
        requirement: RequirementSpec,
        template: TemplateSpec,
    ) -> OutlineSpec:
        if not template.slide_structure:
            raise OutlineBuildError("Template slide_structure must not be empty")

        slides = [
            self._build_item(index=index, role=role)
            for index, role in enumerate(
                self._roles_for_slide_count(
                    template.slide_structure,
                    requirement.slide_count,
                ),
                start=1,
            )
        ]

        return OutlineSpec(title=requirement.theme, slides=slides)

    def _roles_for_slide_count(
        self,
        slide_structure: list[str],
        slide_count: int,
    ) -> list[str]:
        roles: list[str] = []
        for index in range(slide_count):
            roles.append(slide_structure[index % len(slide_structure)])
        return roles

    def _build_item(self, index: int, role: str) -> OutlineItem:
        return OutlineItem(
            slide_id=f"slide-{index:03d}",
            title=role,
            role=role,
        )
