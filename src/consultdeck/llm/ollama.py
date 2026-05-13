from __future__ import annotations

from typing import Any

import httpx

from consultdeck.llm.parser import LlmResponseParser
from consultdeck.llm.prompt import LlmPromptBuilder
from consultdeck.llm.protocol import LlmParseError
from consultdeck.llm.request import LlmGenerationRequest, LlmGenerationResult


class OllamaLlmProvider:
    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "gemma4:latest",
        timeout_seconds: float = 30.0,
        prompt_builder: LlmPromptBuilder | Any | None = None,
        response_parser: LlmResponseParser | Any | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.prompt_builder = prompt_builder or LlmPromptBuilder()
        self.response_parser = response_parser or LlmResponseParser()
        self.transport = transport

    def generate_slide_content(
        self,
        request: LlmGenerationRequest,
    ) -> LlmGenerationResult:
        prompt = self.prompt_builder.build(request)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        with httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            transport=self.transport,
        ) as client:
            response = client.post("/api/generate", json=payload)
            response.raise_for_status()
            raw = self._extract_response_text(response)
            return self.response_parser.parse(raw)

    def _extract_response_text(self, response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError as exc:
            raise LlmParseError("Ollama response must be valid JSON") from exc

        if not isinstance(payload, dict):
            raise LlmParseError("Ollama response must be a JSON object")

        raw = payload.get("response")
        if not isinstance(raw, str) or not raw:
            raise LlmParseError("Ollama response must include response text")
        return raw
