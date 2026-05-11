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
