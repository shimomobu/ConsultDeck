from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.models.template_spec import TemplateSpec
from consultdeck.template.selector import TemplateSelector


def _requirement(purpose: str, audience: str = "経営層") -> RequirementSpec:
    return RequirementSpec(
        theme="DX推進",
        purpose=purpose,
        audience=audience,
        slide_count=5,
    )


def _template(template_id: str, doc_type: str, audience: str = "経営層") -> TemplateSpec:
    return TemplateSpec(
        template_id=template_id,
        name=template_id,
        doc_type=doc_type,
        use_case=doc_type,
        audience=audience,
        phase=doc_type,
        slide_structure=["導入", "本論"],
    )


def test_selector_matches_japanese_purpose_to_english_doc_type() -> None:
    selector = TemplateSelector()
    templates = [_template("proposal_standard", "proposal")]

    matches = selector.find_matches(_requirement("提案"), templates)

    assert [template.template_id for template in matches] == ["proposal_standard"]


def test_selector_matches_english_purpose_to_japanese_doc_type() -> None:
    selector = TemplateSelector()
    templates = [_template("report_standard", "報告書")]

    matches = selector.find_matches(_requirement("report"), templates)

    assert [template.template_id for template in matches] == ["report_standard"]


def test_selector_treats_analysis_synonyms_as_same_doc_type() -> None:
    selector = TemplateSelector()
    templates = [_template("analysis_standard", "analysis")]

    matches = selector.find_matches(_requirement("調査分析"), templates)

    assert [template.template_id for template in matches] == ["analysis_standard"]


def test_selector_keeps_audience_as_exact_match() -> None:
    selector = TemplateSelector()
    templates = [_template("proposal_standard", "proposal", audience="部長層")]

    matches = selector.find_matches(_requirement("提案", audience="経営層"), templates)

    assert matches == []


def test_selector_returns_only_matching_templates_from_multiple_candidates() -> None:
    selector = TemplateSelector()
    templates = [
        _template("proposal_standard", "提案書"),
        _template("analysis_standard", "analysis"),
        _template("report_standard", "報告書", audience="部長層"),
    ]

    matches = selector.find_matches(_requirement("proposal"), templates)

    assert [template.template_id for template in matches] == ["proposal_standard"]


def test_selector_returns_empty_list_when_no_doc_type_matches() -> None:
    selector = TemplateSelector()
    templates = [_template("proposal_standard", "proposal")]

    matches = selector.find_matches(_requirement("workshop"), templates)

    assert matches == []
