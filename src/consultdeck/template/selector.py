from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.models.template_spec import TemplateSpec


class TemplateSelector:
    _DOC_TYPE_ALIASES = {
        "proposal": {"proposal", "提案", "提案書"},
        "analysis": {"analysis", "分析", "調査分析"},
        "report": {"report", "報告", "報告書"},
    }

    def find_matches(
        self,
        requirement: RequirementSpec,
        templates: list[TemplateSpec],
    ) -> list[TemplateSpec]:
        requirement_doc_type = self._normalize_doc_type(requirement.purpose)
        requirement_audience = self._normalize_audience(requirement.audience)

        return [
            template
            for template in templates
            if self._normalize_doc_type(template.doc_type) == requirement_doc_type
            and self._normalize_audience(template.audience) == requirement_audience
        ]

    def _normalize_doc_type(self, value: str) -> str:
        normalized = value.strip().casefold()
        for canonical, aliases in self._DOC_TYPE_ALIASES.items():
            if normalized in {alias.casefold() for alias in aliases}:
                return canonical
        return normalized

    def _normalize_audience(self, value: str) -> str:
        # MVP keeps audience matching intentionally strict: trim + casefold only.
        return value.strip().casefold()
