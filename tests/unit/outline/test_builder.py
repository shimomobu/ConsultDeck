import pytest

from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.models.template_spec import TemplateSpec
from consultdeck.outline.builder import OutlineBuildError, OutlineBuilder


def _requirement(slide_count: int = 3) -> RequirementSpec:
    return RequirementSpec(
        theme="DX推進",
        purpose="提案",
        audience="経営層",
        slide_count=slide_count,
    )


def _template(slide_structure: list[str]) -> TemplateSpec:
    return TemplateSpec(
        template_id="proposal_standard",
        name="Proposal Standard",
        doc_type="proposal",
        use_case="提案書",
        audience="経営層",
        phase="proposal",
        slide_structure=slide_structure,
    )


def test_builder_creates_outline_from_requirement_and_template() -> None:
    builder = OutlineBuilder()

    outline = builder.build(_requirement(), _template(["課題", "解決策", "効果"]))

    assert outline.title == "DX推進"
    assert [(slide.slide_id, slide.title, slide.role) for slide in outline.slides] == [
        ("slide-001", "課題", "課題"),
        ("slide-002", "解決策", "解決策"),
        ("slide-003", "効果", "効果"),
    ]


def test_builder_preserves_slide_structure_order() -> None:
    builder = OutlineBuilder()

    outline = builder.build(_requirement(), _template(["現状", "論点", "対応"]))

    assert [slide.role for slide in outline.slides] == ["現状", "論点", "対応"]


def test_builder_repeats_structure_when_slide_count_is_larger() -> None:
    builder = OutlineBuilder()

    outline = builder.build(_requirement(slide_count=5), _template(["課題", "解決策"]))

    assert [(slide.slide_id, slide.role) for slide in outline.slides] == [
        ("slide-001", "課題"),
        ("slide-002", "解決策"),
        ("slide-003", "課題"),
        ("slide-004", "解決策"),
        ("slide-005", "課題"),
    ]


def test_builder_truncates_structure_when_slide_count_is_smaller() -> None:
    builder = OutlineBuilder()

    outline = builder.build(
        _requirement(slide_count=2),
        _template(["課題", "解決策", "効果"]),
    )

    assert [slide.role for slide in outline.slides] == ["課題", "解決策"]


def test_builder_raises_when_template_slide_structure_is_empty() -> None:
    builder = OutlineBuilder()
    template = _template(["placeholder"])
    template.slide_structure.clear()

    with pytest.raises(OutlineBuildError):
        builder.build(_requirement(), template)


def test_builder_output_is_renderer_independent() -> None:
    builder = OutlineBuilder()

    outline = builder.build(_requirement(), _template(["課題"]))

    assert "renderer" not in outline.model_dump()
    assert "pptx" not in outline.model_dump()
