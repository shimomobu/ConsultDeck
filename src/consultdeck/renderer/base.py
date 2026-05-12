from pathlib import Path
from typing import Protocol

from consultdeck.models.slide_spec import SlideSpec


class Renderer(Protocol):
    def render(
        self,
        spec: SlideSpec,
        output_dir: Path,
    ) -> Path:
        """Render a SlideSpec into an output artifact."""
