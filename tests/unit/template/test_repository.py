import pytest

from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.models.template_spec import TemplateSpec
from consultdeck.template.repository import (
    TemplateLoadError,
    TemplateNotFoundError,
    TemplateRepository,
)


PROPOSAL_YAML = """
template_id: proposal_standard
name: Proposal Standard
doc_type: proposal
use_case: 提案書
audience: 経営層
phase: proposal
slide_structure:
  - 課題
  - 解決策
  - 効果
"""


REPORT_YAML = """
template_id: report_standard
name: Report Standard
doc_type: report
use_case: 報告書
audience: 部長層
phase: reporting
slide_structure:
  - 状況
  - 課題
  - 対応
"""


def test_repository_loads_template_spec_from_yaml(tmp_path) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "proposal_standard.yaml").write_text(PROPOSAL_YAML, encoding="utf-8")

    repository = TemplateRepository(template_dir)
    spec = repository.get("proposal_standard")

    assert isinstance(spec, TemplateSpec)
    assert spec.template_id == "proposal_standard"
    assert spec.slide_structure == ["課題", "解決策", "効果"]


def test_repository_loads_multiple_templates(tmp_path) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "proposal_standard.yaml").write_text(PROPOSAL_YAML, encoding="utf-8")
    (template_dir / "report_standard.yaml").write_text(REPORT_YAML, encoding="utf-8")

    repository = TemplateRepository(template_dir)
    templates = repository.list()

    assert [template.template_id for template in templates] == [
        "proposal_standard",
        "report_standard",
    ]


def test_repository_finds_templates_matching_requirement(tmp_path) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "proposal_standard.yaml").write_text(PROPOSAL_YAML, encoding="utf-8")
    (template_dir / "report_standard.yaml").write_text(REPORT_YAML, encoding="utf-8")
    requirement = RequirementSpec(
        theme="DX推進",
        purpose="proposal",
        audience="経営層",
        slide_count=5,
    )

    repository = TemplateRepository(template_dir)
    matches = repository.find_matches(requirement)

    assert [template.template_id for template in matches] == ["proposal_standard"]


def test_repository_find_matches_uses_normalized_doc_type_matching(tmp_path) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "proposal_standard.yaml").write_text(PROPOSAL_YAML, encoding="utf-8")
    requirement = RequirementSpec(
        theme="DX推進",
        purpose="提案書",
        audience="経営層",
        slide_count=5,
    )

    repository = TemplateRepository(template_dir)
    matches = repository.find_matches(requirement)

    assert [template.template_id for template in matches] == ["proposal_standard"]


def test_repository_returns_empty_list_when_no_template_matches(tmp_path) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "proposal_standard.yaml").write_text(PROPOSAL_YAML, encoding="utf-8")
    requirement = RequirementSpec(
        theme="DX推進",
        purpose="analysis",
        audience="現場",
        slide_count=5,
    )

    repository = TemplateRepository(template_dir)

    assert repository.find_matches(requirement) == []


def test_repository_raises_for_missing_template_id(tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")

    with pytest.raises(TemplateNotFoundError):
        repository.get("missing")


def test_repository_detects_invalid_yaml(tmp_path) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "broken.yaml").write_text("template_id: [", encoding="utf-8")

    repository = TemplateRepository(template_dir)

    with pytest.raises(TemplateLoadError):
        repository.list()
