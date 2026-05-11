import pytest

from consultdeck.models.outline_spec import OutlineItem, OutlineSpec
from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.models.slide_spec import LayoutType, SlideSpec
from consultdeck.models.template_spec import TemplateSpec
from consultdeck.slide.builder import SlideBuildError, SlideBuilder


def _requirement() -> RequirementSpec:
    return RequirementSpec(
        theme="DX推進",
        purpose="提案",
        audience="経営層",
        slide_count=3,
    )


def _outline(slides: list[OutlineItem] | None = None) -> OutlineSpec:
    return OutlineSpec(
        title="DX推進",
        slides=slides
        if slides is not None
        else [
            OutlineItem(slide_id="slide-001", title="課題", role="課題"),
            OutlineItem(slide_id="slide-002", title="解決策", role="解決策"),
            OutlineItem(slide_id="slide-003", title="効果", role="効果"),
        ],
    )


def _template() -> TemplateSpec:
    return TemplateSpec(
        template_id="proposal_standard",
        name="Proposal Standard",
        doc_type="proposal",
        use_case="提案書",
        audience="経営層",
        phase="proposal",
        slide_structure=["課題", "解決策", "効果"],
        layout_rules={},
        style_rules={},
        output_targets=["pptx"],
    )


def test_builder_creates_slide_spec_from_outline() -> None:
    builder = SlideBuilder()

    spec = builder.build(_requirement(), _outline(), _template(), deck_id="deck-test")

    assert isinstance(spec, SlideSpec)
    assert spec.deck_id == "deck-test"
    assert spec.title == "DX推進"
    assert spec.template_id == "proposal_standard"
    assert len(spec.slides) == 3


def test_builder_generates_unique_deck_id_when_not_provided() -> None:
    builder = SlideBuilder()

    first = builder.build(_requirement(), _outline(), _template())
    second = builder.build(_requirement(), _outline(), _template())

    assert first.deck_id.startswith("deck-")
    assert second.deck_id.startswith("deck-")
    assert first.deck_id != second.deck_id


def test_builder_inherits_slide_id_and_title_from_outline_items() -> None:
    builder = SlideBuilder()

    spec = builder.build(_requirement(), _outline(), _template())

    assert [(slide.slide_id, slide.title) for slide in spec.slides] == [
        ("slide-001", "課題"),
        ("slide-002", "解決策"),
        ("slide-003", "効果"),
    ]


def test_builder_keeps_slide_count_equal_to_outline_items() -> None:
    builder = SlideBuilder()
    outline = _outline(
        [
            OutlineItem(slide_id="slide-001", title="課題", role="課題"),
            OutlineItem(slide_id="slide-002", title="解決策", role="解決策"),
        ]
    )

    spec = builder.build(_requirement(), outline, _template())

    assert len(spec.slides) == 2


def test_builder_generates_bullets_for_content_and_two_column_layouts() -> None:
    builder = SlideBuilder()
    outline = _outline(
        [
            OutlineItem(slide_id="slide-001", title="比較", role="比較"),
            OutlineItem(slide_id="slide-002", title="課題", role="課題"),
        ]
    )

    spec = builder.build(_requirement(), outline, _template())

    assert all(slide.bullets for slide in spec.slides)


def test_builder_allows_title_layout_without_bullets() -> None:
    builder = SlideBuilder()
    outline = _outline([OutlineItem(slide_id="slide-001", title="表紙", role="表紙")])

    spec = builder.build(_requirement(), outline, _template())

    assert spec.slides[0].layout_type is LayoutType.TITLE
    assert spec.slides[0].bullets == []


def test_builder_sets_layout_type_from_role() -> None:
    builder = SlideBuilder()
    outline = _outline(
        [
            OutlineItem(slide_id="slide-001", title="表紙", role="表紙"),
            OutlineItem(slide_id="slide-002", title="比較", role="比較"),
            OutlineItem(slide_id="slide-003", title="課題", role="課題"),
        ]
    )

    spec = builder.build(_requirement(), outline, _template())

    assert [slide.layout_type for slide in spec.slides] == [
        LayoutType.TITLE,
        LayoutType.TWO_COLUMN,
        LayoutType.CONTENT,
    ]


def test_builder_output_is_renderer_independent() -> None:
    builder = SlideBuilder()

    spec = builder.build(_requirement(), _outline(), _template())

    assert "renderer" not in spec.model_dump()
    assert "pptx" not in spec.model_dump()


def test_builder_raises_when_outline_has_no_slides() -> None:
    builder = SlideBuilder()

    with pytest.raises(SlideBuildError):
        builder.build(_requirement(), _outline([]), _template())
