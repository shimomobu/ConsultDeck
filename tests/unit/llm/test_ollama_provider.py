import json

import httpx
import pytest

from consultdeck.__main__ import _build_parser
from consultdeck.llm.ollama import OllamaLlmProvider
from consultdeck.llm.protocol import LlmParseError
from consultdeck.llm.provider_factory import build_llm_provider
from consultdeck.llm.request import (
    LlmGenerationRequest,
    LlmGenerationResult,
    LlmTemplateContext,
)
from consultdeck.models.outline_spec import OutlineItem, OutlineSpec
from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.models.template_spec import TemplateSpec


def _request() -> LlmGenerationRequest:
    template = TemplateSpec(
        template_id="proposal_standard",
        name="Proposal Standard",
        doc_type="proposal",
        use_case="提案書",
        audience="経営層",
        phase="proposal",
        slide_structure=["課題", "効果"],
        layout_rules={},
        style_rules={"tone": "formal"},
        output_targets=["pptx"],
    )
    return LlmGenerationRequest(
        requirement=RequirementSpec(
            theme="DX推進",
            purpose="proposal",
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
        template_context=LlmTemplateContext.from_template(template),
    )


def test_ollama_provider_posts_generate_request_and_parses_response() -> None:
    request = _request()

    def handler(http_request: httpx.Request) -> httpx.Response:
        assert http_request.method == "POST"
        assert http_request.url == httpx.URL("http://ollama.local:11434/api/generate")
        payload = json.loads(http_request.content.decode("utf-8"))
        assert payload["model"] == "gemma4:latest"
        assert payload["stream"] is False
        assert "Theme: DX推進" in payload["prompt"]
        return httpx.Response(
            200,
            json={
                "response": json.dumps(
                    {
                        "slides": [
                            {
                                "slide_id": "slide-001",
                                "message": "Ollama generated message",
                                "bullets": ["bullet 1"],
                                "notes": "speaker note",
                            }
                        ]
                    }
                ),
                "done": True,
            },
        )

    provider = OllamaLlmProvider(
        base_url="http://ollama.local:11434",
        transport=httpx.MockTransport(handler),
    )

    result = provider.generate_slide_content(request)

    assert result.slides[0].message == "Ollama generated message"
    assert result.slides[0].bullets == ["bullet 1"]


def test_ollama_provider_uses_injected_prompt_builder_and_parser() -> None:
    class StubPromptBuilder:
        def __init__(self) -> None:
            self.received_request: LlmGenerationRequest | None = None

        def build(self, request: LlmGenerationRequest) -> str:
            self.received_request = request
            return "PROMPT FROM STUB"

    class StubParser:
        def __init__(self) -> None:
            self.received_raw: str | None = None

        def parse(self, raw: str) -> LlmGenerationResult:
            self.received_raw = raw
            return LlmGenerationResult(slides=[])

    prompt_builder = StubPromptBuilder()
    parser = StubParser()

    def handler(http_request: httpx.Request) -> httpx.Response:
        payload = json.loads(http_request.content.decode("utf-8"))
        assert payload["prompt"] == "PROMPT FROM STUB"
        return httpx.Response(200, json={"response": "RAW MODEL OUTPUT", "done": True})

    provider = OllamaLlmProvider(
        prompt_builder=prompt_builder,
        response_parser=parser,
        transport=httpx.MockTransport(handler),
    )

    result = provider.generate_slide_content(_request())

    assert result.slides == []
    assert prompt_builder.received_request is not None
    assert parser.received_raw == "RAW MODEL OUTPUT"


def test_ollama_provider_finishes_response_parsing_before_client_exit(
    monkeypatch,
) -> None:
    state = {"closed": False}

    class StubResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, str]:
            if state["closed"]:
                raise AssertionError("response.json() called after client exit")
            return {"response": "RAW MODEL OUTPUT"}

    class StubClient:
        def __init__(self, *, base_url, timeout, transport) -> None:
            self.base_url = base_url
            self.timeout = timeout
            self.transport = transport

        def __enter__(self):
            state["closed"] = False
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            state["closed"] = True
            return None

        def post(self, url: str, json: dict[str, object]) -> StubResponse:
            return StubResponse()

    class StubParser:
        def parse(self, raw: str) -> LlmGenerationResult:
            if state["closed"]:
                raise AssertionError("parser.parse() called after client exit")
            assert raw == "RAW MODEL OUTPUT"
            return LlmGenerationResult(slides=[])

    monkeypatch.setattr("consultdeck.llm.ollama.httpx.Client", StubClient)

    provider = OllamaLlmProvider(response_parser=StubParser())

    result = provider.generate_slide_content(_request())

    assert result.slides == []
    assert state["closed"] is True


def test_ollama_provider_propagates_http_errors() -> None:
    def handler(http_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection failed", request=http_request)

    provider = OllamaLlmProvider(transport=httpx.MockTransport(handler))

    with pytest.raises(httpx.HTTPError):
        provider.generate_slide_content(_request())


def test_ollama_provider_uses_configured_http_timeout(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class StubClient:
        def __init__(self, *, base_url, timeout, transport) -> None:
            captured["base_url"] = base_url
            captured["timeout"] = timeout
            captured["transport"] = transport

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

        def post(self, url: str, json: dict[str, object]) -> httpx.Response:
            return httpx.Response(
                200,
                request=httpx.Request("POST", f"http://127.0.0.1:11434{url}"),
                json={
                    "response": '{"slides": [{"slide_id": "slide-001", "message": "ok"}]}',
                    "done": True,
                },
            )

    monkeypatch.setattr("consultdeck.llm.ollama.httpx.Client", StubClient)

    provider = OllamaLlmProvider(timeout_seconds=12.5)

    provider.generate_slide_content(_request())

    assert captured["base_url"] == "http://127.0.0.1:11434"
    assert captured["timeout"] == 12.5


def test_ollama_provider_maps_malformed_response_to_parse_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": "not-json", "done": True})

    provider = OllamaLlmProvider(transport=httpx.MockTransport(handler))

    with pytest.raises(LlmParseError):
        provider.generate_slide_content(_request())


def test_ollama_provider_rejects_missing_response_field() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"done": True})

    provider = OllamaLlmProvider(transport=httpx.MockTransport(handler))

    with pytest.raises(LlmParseError, match="response text"):
        provider.generate_slide_content(_request())


def test_llm_provider_factory_builds_ollama_provider() -> None:
    assert isinstance(build_llm_provider("ollama"), OllamaLlmProvider)


def test_llm_provider_factory_passes_model_to_ollama_provider() -> None:
    provider = build_llm_provider("ollama", model_name="gemma4:latest")

    assert isinstance(provider, OllamaLlmProvider)
    assert provider.model == "gemma4:latest"


def test_llm_provider_factory_ignores_model_for_none_and_fake() -> None:
    assert build_llm_provider("none", model_name="gemma4:latest") is None
    assert build_llm_provider("fake", model_name="gemma4:latest") is not None


def test_cli_accepts_ollama_llm_provider_choice() -> None:
    parser = _build_parser()
    args = parser.parse_args(
        [
            "--topic",
            "DX推進",
            "--purpose",
            "proposal",
            "--audience",
            "経営層",
            "--slides",
            "2",
            "--output",
            "output",
            "--llm-provider",
            "ollama",
        ]
    )

    assert args.llm_provider == "ollama"


def test_cli_accepts_llm_model_for_ollama() -> None:
    parser = _build_parser()
    args = parser.parse_args(
        [
            "--topic",
            "DX推進",
            "--purpose",
            "proposal",
            "--audience",
            "経営層",
            "--slides",
            "2",
            "--output",
            "output",
            "--llm-provider",
            "ollama",
            "--llm-model",
            "gemma4:latest",
        ]
    )

    assert args.llm_provider == "ollama"
    assert args.llm_model == "gemma4:latest"


def test_cli_defaults_llm_model_without_affecting_non_ollama_providers() -> None:
    parser = _build_parser()
    args = parser.parse_args(
        [
            "--topic",
            "DX推進",
            "--purpose",
            "proposal",
            "--audience",
            "経営層",
            "--slides",
            "2",
            "--output",
            "output",
            "--llm-provider",
            "fake",
        ]
    )

    assert args.llm_provider == "fake"
    assert args.llm_model == "gemma4:latest"
