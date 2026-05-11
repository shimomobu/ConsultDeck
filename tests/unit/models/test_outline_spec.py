from consultdeck.models.outline_spec import OutlineSpec, Section


def test_outline_spec_accepts_sections() -> None:
    spec = OutlineSpec(
        title="DX推進提案",
        sections=[
            Section(
                section_title="課題",
                slide_titles=["現状課題", "影響"],
            )
        ],
    )

    assert spec.title == "DX推進提案"
    assert spec.sections[0].section_title == "課題"
    assert spec.sections[0].slide_titles == ["現状課題", "影響"]
