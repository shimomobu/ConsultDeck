import yaml
import pytest
from pydantic import ValidationError

from consultdeck.models.slide_spec import LayoutType, Slide, SlideSpec


def _sample_slide_spec() -> SlideSpec:
    return SlideSpec(
        deck_id="deck-001",
        title="DX推進提案",
        template_id="proposal_standard",
        slides=[
            Slide(
                slide_id="slide-001",
                title="現状課題",
                message="属人化により意思決定が遅延している",
                bullets=["情報が分散している", "承認に時間がかかる"],
                layout_type=LayoutType.CONTENT,
                notes="経営層向けに影響を強調する",
            )
        ],
    )


def test_slide_spec_accepts_layout_type_enum() -> None:
    spec = _sample_slide_spec()

    assert spec.slides[0].layout_type is LayoutType.CONTENT


def test_slide_spec_rejects_unknown_layout_type() -> None:
    with pytest.raises(ValidationError):
        SlideSpec(
            deck_id="deck-001",
            title="DX推進提案",
            template_id="proposal_standard",
            slides=[
                {
                    "slide_id": "slide-001",
                    "title": "現状課題",
                    "message": "属人化により意思決定が遅延している",
                    "bullets": [],
                    "layout_type": "unknown",
                }
            ],
        )


def test_slide_allows_empty_bullets() -> None:
    slide = Slide(
        slide_id="slide-001",
        title="表紙",
        message="DX推進提案",
        bullets=[],
        layout_type=LayoutType.TITLE,
    )

    assert slide.bullets == []


def test_slide_spec_rejects_empty_slides() -> None:
    with pytest.raises(ValidationError):
        SlideSpec(
            deck_id="deck-001",
            title="DX推進提案",
            template_id="proposal_standard",
            slides=[],
        )


def test_slide_spec_json_roundtrip() -> None:
    spec = _sample_slide_spec()

    restored = SlideSpec.model_validate_json(spec.model_dump_json())

    assert restored == spec


def test_slide_spec_yaml_roundtrip() -> None:
    spec = _sample_slide_spec()

    raw = yaml.safe_dump(spec.model_dump(mode="json"), allow_unicode=True)
    restored = SlideSpec.model_validate(yaml.safe_load(raw))

    assert restored == spec
