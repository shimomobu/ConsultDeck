import pytest
from pydantic import ValidationError

from consultdeck.models.template_spec import TemplateSpec


def test_template_spec_accepts_required_fields() -> None:
    spec = TemplateSpec(
        template_id="proposal_standard",
        name="Proposal Standard",
        doc_type="proposal",
        use_case="提案書",
        audience="経営層",
        phase="proposal",
        slide_structure=["課題", "解決策", "効果"],
    )

    assert spec.template_id == "proposal_standard"
    assert spec.name == "Proposal Standard"
    assert spec.doc_type == "proposal"
    assert spec.slide_structure == ["課題", "解決策", "効果"]


def test_template_spec_rejects_blank_template_id() -> None:
    with pytest.raises(ValidationError):
        TemplateSpec(
            template_id=" ",
            name="Proposal Standard",
            doc_type="proposal",
            use_case="提案書",
            audience="経営層",
            phase="proposal",
            slide_structure=["課題", "解決策", "効果"],
        )
