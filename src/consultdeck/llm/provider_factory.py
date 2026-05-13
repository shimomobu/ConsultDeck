from __future__ import annotations

from consultdeck.llm.fake import FakeLlmProvider
from consultdeck.llm.protocol import LlmProvider
from consultdeck.llm.request import GeneratedSlideContent, LlmGenerationResult


def build_llm_provider(provider_name: str) -> LlmProvider | None:
    if provider_name == "none":
        return None
    if provider_name == "fake":
        return FakeLlmProvider(
            LlmGenerationResult(
                slides=[
                    GeneratedSlideContent(
                        slide_id="slide-001",
                        message="Fake provider generated message",
                        bullets=["Fake provider bullet"],
                        notes="Fake provider notes",
                    )
                ]
            )
        )

    raise ValueError(f"Unsupported llm provider: {provider_name}")
