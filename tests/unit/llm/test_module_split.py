import pytest

from consultdeck.llm.fake import FakeLlmProvider
from consultdeck.llm.parser import LlmResponseParser
from consultdeck.llm.prompt import LlmPromptBuilder
from consultdeck.llm.protocol import LlmParseError
from consultdeck.llm.request import (
    GeneratedSlideContent,
    LlmGenerationRequest,
    LlmGenerationResult,
    LlmTemplateContext,
)
from consultdeck.models.outline_spec import OutlineItem, OutlineSpec
from consultdeck.models.requirement_spec import RequirementSpec


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


def test_llm_prompt_builder_is_available_under_consultdeck_llm() -> None:
    prompt = LlmPromptBuilder().build(_request())

    assert "Theme: DX推進" in prompt
    assert '"slides"' in prompt


def test_llm_response_parser_is_available_under_consultdeck_llm() -> None:
    result = LlmResponseParser().parse(
        '{"slides": [{"slide_id": "slide-001", "message": "LLM message"}]}'
    )

    assert result.slides[0].slide_id == "slide-001"
    assert result.slides[0].message == "LLM message"


def test_llm_response_parser_raises_protocol_error_under_consultdeck_llm() -> None:
    with pytest.raises(LlmParseError):
        LlmResponseParser().parse("{}")


def test_fake_provider_is_available_under_consultdeck_llm() -> None:
    provider = FakeLlmProvider(
        LlmGenerationResult(
            slides=[
                GeneratedSlideContent(
                    slide_id="slide-001",
                    message="Fake provider generated message",
                )
            ]
        )
    )

    assert provider.generate_slide_content(_request()).slides[0].message == (
        "Fake provider generated message"
    )
