"""LLM provider integration helpers."""

from consultdeck.llm.fake import FakeLlmProvider
from consultdeck.llm.ollama import OllamaLlmProvider
from consultdeck.llm.parser import LlmResponseParser
from consultdeck.llm.prompt import LlmPromptBuilder
from consultdeck.llm.protocol import LlmParseError, LlmProvider
from consultdeck.llm.request import (
    GeneratedSlideContent,
    LlmGenerationRequest,
    LlmGenerationResult,
    LlmTemplateContext,
)

__all__ = [
    "FakeLlmProvider",
    "GeneratedSlideContent",
    "LlmGenerationRequest",
    "LlmGenerationResult",
    "LlmParseError",
    "OllamaLlmProvider",
    "LlmPromptBuilder",
    "LlmProvider",
    "LlmResponseParser",
    "LlmTemplateContext",
]
