from __future__ import annotations

from typing import Protocol

from consultdeck.llm.request import LlmGenerationRequest, LlmGenerationResult


class LlmParseError(ValueError):
    """Raised when provider response text cannot be parsed into LLM content."""


class LlmProvider(Protocol):
    def generate_slide_content(
        self,
        request: LlmGenerationRequest,
    ) -> LlmGenerationResult:
        """Generate slide body content for a structured request."""
