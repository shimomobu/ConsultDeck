from enum import StrEnum
from typing import Annotated, Any

from pydantic import BaseModel, Field, StringConstraints

NonBlankString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class LayoutType(StrEnum):
    TITLE = "title"
    CONTENT = "content"
    TWO_COLUMN = "two_column"
    BLANK = "blank"


class DiagramSpec(BaseModel):
    diagram_type: NonBlankString
    data: dict[str, Any] = Field(default_factory=dict)


class ImageSpec(BaseModel):
    prompt: NonBlankString
    path: str | None = None
    size: str | None = None


class Slide(BaseModel):
    slide_id: NonBlankString
    title: NonBlankString
    message: NonBlankString
    bullets: list[str] = Field(default_factory=list)
    diagram: DiagramSpec | None = None
    image: ImageSpec | None = None
    notes: str | None = None
    layout_type: LayoutType


class SlideSpec(BaseModel):
    deck_id: NonBlankString
    title: NonBlankString
    template_id: NonBlankString
    slides: list[Slide] = Field(min_length=1)
