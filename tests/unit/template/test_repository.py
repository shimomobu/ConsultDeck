import pytest

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
layout_rules:
  default: content
style_rules:
  font: Arial
output_targets:
  - pptx
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
layout_rules:
  default: content
style_rules:
  font: Arial
output_targets:
  - pptx
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


def test_repository_does_not_expose_matching_behavior(tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")

    assert not hasattr(repository, "find_matches")


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


def test_repository_converts_validation_error_to_template_load_error(tmp_path) -> None:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "invalid_spec.yaml").write_text(
        """
template_id: invalid
name: Invalid Template
doc_type: proposal
use_case: 提案書
audience: 経営層
phase: proposal
slide_structure: []
layout_rules: {}
style_rules: {}
output_targets:
  - pptx
""",
        encoding="utf-8",
    )

    repository = TemplateRepository(template_dir)

    with pytest.raises(TemplateLoadError):
        repository.list()
