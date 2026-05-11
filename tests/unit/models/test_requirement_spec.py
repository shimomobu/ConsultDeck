import pytest
from pydantic import ValidationError

from consultdeck.models.requirement_spec import RequirementSpec


def test_requirement_spec_accepts_required_fields() -> None:
    spec = RequirementSpec(
        theme="DX推進",
        purpose="提案",
        audience="経営層",
        slide_count=5,
    )

    assert spec.theme == "DX推進"
    assert spec.purpose == "提案"
    assert spec.audience == "経営層"
    assert spec.slide_count == 5
    assert spec.tone == "formal"
    assert spec.constraints is None
    assert spec.template_id is None


def test_slide_count_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        RequirementSpec(
            theme="DX推進",
            purpose="提案",
            audience="経営層",
            slide_count=0,
        )


def test_theme_must_not_be_blank() -> None:
    with pytest.raises(ValidationError):
        RequirementSpec(
            theme=" ",
            purpose="提案",
            audience="経営層",
            slide_count=5,
        )
