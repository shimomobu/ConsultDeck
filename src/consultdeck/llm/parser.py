from __future__ import annotations

import json

from consultdeck.llm.protocol import LlmParseError
from consultdeck.llm.request import GeneratedSlideContent, LlmGenerationResult


class LlmResponseParser:
    def parse(self, raw: str) -> LlmGenerationResult:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LlmParseError("LLM response must be valid JSON") from exc

        if not isinstance(payload, dict):
            raise LlmParseError("LLM response must be a JSON object")

        raw_slides = payload.get("slides")
        if not isinstance(raw_slides, list):
            raise LlmParseError("LLM response must include a slides list")

        slides = [self._parse_slide(item) for item in raw_slides]
        return LlmGenerationResult(slides=slides)

    def _parse_slide(self, raw: object) -> GeneratedSlideContent:
        if not isinstance(raw, dict):
            raise LlmParseError("Each slide must be a JSON object")

        slide_id = raw.get("slide_id")
        message = raw.get("message")
        bullets = raw.get("bullets", [])
        notes = raw.get("notes")

        if not isinstance(slide_id, str) or not slide_id:
            raise LlmParseError("Each slide requires a string slide_id")
        if not isinstance(message, str) or not message:
            raise LlmParseError("Each slide requires a string message")
        if not isinstance(bullets, list) or not all(
            isinstance(bullet, str) for bullet in bullets
        ):
            raise LlmParseError("Slide bullets must be a list of strings")
        if notes is not None and not isinstance(notes, str):
            raise LlmParseError("Slide notes must be a string or null")

        return GeneratedSlideContent(
            slide_id=slide_id,
            message=message,
            bullets=bullets,
            notes=notes,
        )
