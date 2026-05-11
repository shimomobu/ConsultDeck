from pathlib import Path
from typing import Protocol

from consultdeck.models.slide_spec import SlideSpec
from consultdeck.models.template_spec import TemplateSpec


class Renderer(Protocol):
    def render(
        self,
        spec: SlideSpec,
        template: TemplateSpec,
        output_dir: Path,
    ) -> Path:
        """Render a SlideSpec into an output artifact."""
