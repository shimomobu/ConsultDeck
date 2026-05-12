from consultdeck.models.outline_spec import OutlineItem, OutlineSpec
from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.slide.content_generator import (
    LlmGenerationRequest,
    LlmPromptBuilder,
    LlmTemplateContext,
)


def _request() -> LlmGenerationRequest:
    return LlmGenerationRequest(
        requirement=RequirementSpec(
            theme="DX推進",
            purpose="提案",
            audience="経営層",
            slide_count=2,
            tone="formal",
        ),
        outline=OutlineSpec(
            title="DX推進提案",
            slides=[
                OutlineItem(slide_id="slide-001", title="課題", role="課題"),
                OutlineItem(slide_id="slide-002", title="効果", role="効果"),
            ],
        ),
        template_context=LlmTemplateContext(
            template_id="proposal_standard",
            doc_type="proposal",
            use_case="提案書",
            audience="経営層",
            phase="proposal",
            style_rules={"font": "Arial", "tone": "formal"},
        ),
    )


def test_prompt_builder_generates_deterministic_prompt() -> None:
    builder = LlmPromptBuilder()
    request = _request()

    assert builder.build(request) == builder.build(request)


def test_prompt_builder_includes_minimum_generation_context() -> None:
    prompt = LlmPromptBuilder().build(_request())

    assert "Theme: DX推進" in prompt
    assert "Audience: 経営層" in prompt
    assert "Purpose: 提案" in prompt
    assert "Tone: formal" in prompt
    assert "Template: proposal_standard" in prompt
    assert "Doc type: proposal" in prompt
    assert "- slide-001 | title: 課題 | role: 課題" in prompt
    assert "- slide-002 | title: 効果 | role: 効果" in prompt


def test_prompt_builder_requests_json_slide_output() -> None:
    prompt = LlmPromptBuilder().build(_request())

    assert '"slides"' in prompt
    assert '"slide_id"' in prompt
    assert '"message"' in prompt
    assert '"bullets"' in prompt
    assert '"notes"' in prompt
