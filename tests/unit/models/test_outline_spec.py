import pytest
from pydantic import ValidationError

from consultdeck.models.outline_spec import OutlineItem, OutlineSpec


def test_outline_spec_accepts_slide_items() -> None:
    spec = OutlineSpec(
        title="DX推進提案",
        slides=[
            OutlineItem(
                slide_id="slide-001",
                title="課題",
                role="課題",
            )
        ],
    )

    assert spec.title == "DX推進提案"
    assert spec.slides[0].slide_id == "slide-001"
    assert spec.slides[0].title == "課題"
    assert spec.slides[0].role == "課題"


def test_outline_spec_rejects_legacy_sections_field() -> None:
    with pytest.raises(ValidationError):
        OutlineSpec(
            title="DX推進提案",
            sections=[
                {
                    "section_title": "課題",
                    "slide_titles": ["現状課題"],
                }
            ],
        )
