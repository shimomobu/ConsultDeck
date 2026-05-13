from pathlib import Path

from consultdeck.llm.protocol import LlmProvider
from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.outline.builder import OutlineBuilder
from consultdeck.renderer.base import Renderer
from consultdeck.renderer.builtin_pptx_renderer import BuiltinPptxRenderer
from consultdeck.slide.builder import SlideBuilder
from consultdeck.template.repository import TemplateRepository
from consultdeck.template.selector import TemplateSelector


class PipelineError(RuntimeError):
    """Raised when the end-to-end generation pipeline cannot proceed."""


class Pipeline:
    def __init__(
        self,
        template_dir: str | Path,
        template_repository: TemplateRepository | None = None,
        template_selector: TemplateSelector | None = None,
        outline_builder: OutlineBuilder | None = None,
        slide_builder: SlideBuilder | None = None,
        llm_provider: LlmProvider | None = None,
        renderer: Renderer | None = None,
    ) -> None:
        if slide_builder is not None and llm_provider is not None:
            raise ValueError("slide_builder and llm_provider cannot be used together")

        self.template_repository = template_repository or TemplateRepository(template_dir)
        self.template_selector = template_selector or TemplateSelector()
        self.outline_builder = outline_builder or OutlineBuilder()
        self.slide_builder = slide_builder or SlideBuilder(llm_provider=llm_provider)
        self.renderer = renderer or BuiltinPptxRenderer()

    def run(
        self,
        requirement: RequirementSpec,
        output_dir: str | Path,
        deck_id: str | None = None,
    ) -> Path:
        templates = self.template_repository.list()
        matches = self.template_selector.find_matches(requirement, templates)
        if not matches:
            raise PipelineError(
                "No matching template found "
                f"for purpose={requirement.purpose!r}, audience={requirement.audience!r}"
            )

        template = matches[0]
        outline = self.outline_builder.build(requirement, template)
        slide_spec = self.slide_builder.build(
            requirement,
            outline,
            template,
            deck_id=deck_id,
        )
        return self.renderer.render(slide_spec, Path(output_dir))
