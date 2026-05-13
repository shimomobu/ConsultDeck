from __future__ import annotations

from consultdeck.llm.request import LlmGenerationRequest, LlmGenerationResult


class FakeLlmProvider:
    def __init__(self, result: LlmGenerationResult) -> None:
        self.result = result

    def generate_slide_content(
        self,
        request: LlmGenerationRequest,
    ) -> LlmGenerationResult:
        return self.result
