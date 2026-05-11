from pathlib import Path

import pytest
from pptx import Presentation

from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.pipeline.pipeline import Pipeline, PipelineError


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_DIR = PROJECT_ROOT / "assets" / "templates"


def _requirement(
    purpose: str = "proposal",
    audience: str = "経営層",
    slide_count: int = 5,
) -> RequirementSpec:
    return RequirementSpec(
        theme="生成AIの業務活用",
        purpose=purpose,
        audience=audience,
        slide_count=slide_count,
    )


def test_pipeline_generates_pptx(tmp_path) -> None:
    pipeline = Pipeline(template_dir=TEMPLATE_DIR)

    output_path = pipeline.run(_requirement(), tmp_path)

    assert output_path.exists()
    assert output_path.suffix == ".pptx"


def test_pipeline_creates_output_dir(tmp_path) -> None:
    pipeline = Pipeline(template_dir=TEMPLATE_DIR)
    output_dir = tmp_path / "nested" / "output"

    output_path = pipeline.run(_requirement(), output_dir)

    assert output_dir.exists()
    assert output_path.parent == output_dir


def test_pipeline_uses_requested_slide_count(tmp_path) -> None:
    pipeline = Pipeline(template_dir=TEMPLATE_DIR)

    output_path = pipeline.run(_requirement(slide_count=4), tmp_path)

    presentation = Presentation(output_path)
    assert len(presentation.slides) == 4


def test_pipeline_fails_when_no_template_matches(tmp_path) -> None:
    pipeline = Pipeline(template_dir=TEMPLATE_DIR)

    with pytest.raises(PipelineError, match="No matching template"):
        pipeline.run(_requirement(purpose="proposal", audience="現場"), tmp_path)


def test_pipeline_accepts_fixed_deck_id_for_deterministic_output(tmp_path) -> None:
    pipeline = Pipeline(template_dir=TEMPLATE_DIR)

    output_path = pipeline.run(_requirement(), tmp_path, deck_id="deck-cli-test")

    assert output_path == tmp_path / "deck-cli-test.pptx"
