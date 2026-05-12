import pytest

from consultdeck.models.outline_spec import OutlineItem, OutlineSpec
from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.slide.content_generator import (
    LlmParseError,
    LlmGenerationRequest,
    LlmPromptBuilder,
    LlmResponseParser,
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


def test_response_parser_parses_valid_slide_json() -> None:
    raw = """
{
  "slides": [
    {
      "slide_id": "slide-001",
      "message": "LLM message",
      "bullets": ["point 1", "point 2"],
      "notes": "speaker note",
      "ignored": "value"
    }
  ]
}
"""

    result = LlmResponseParser().parse(raw)

    assert len(result.slides) == 1
    assert result.slides[0].slide_id == "slide-001"
    assert result.slides[0].message == "LLM message"
    assert result.slides[0].bullets == ["point 1", "point 2"]
    assert result.slides[0].notes == "speaker note"


def test_response_parser_defaults_optional_bullets_and_notes() -> None:
    raw = '{"slides": [{"slide_id": "slide-001", "message": "LLM message"}]}'

    result = LlmResponseParser().parse(raw)

    assert result.slides[0].bullets == []
    assert result.slides[0].notes is None


@pytest.mark.parametrize(
    "raw",
    [
        "{not json}",
        "{}",
        '{"slides": "not-a-list"}',
        '{"slides": [{"message": "missing slide id"}]}',
        '{"slides": [{"slide_id": "slide-001"}]}',
        '{"slides": [{"slide_id": 1, "message": "bad id"}]}',
        '{"slides": [{"slide_id": "slide-001", "message": 1}]}',
        '{"slides": [{"slide_id": "slide-001", "message": "ok", "bullets": "bad"}]}',
        '{"slides": [{"slide_id": "slide-001", "message": "ok", "bullets": [1]}]}',
        '{"slides": [{"slide_id": "slide-001", "message": "ok", "notes": 1}]}',
    ],
)
def test_response_parser_rejects_malformed_or_invalid_json(raw: str) -> None:
    with pytest.raises(LlmParseError):
        LlmResponseParser().parse(raw)
