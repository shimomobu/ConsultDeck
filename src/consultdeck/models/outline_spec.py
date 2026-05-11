from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

NonBlankString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Section(BaseModel):
    section_title: NonBlankString
    slide_titles: list[NonBlankString] = Field(default_factory=list)


class OutlineItem(BaseModel):
    slide_id: NonBlankString
    title: NonBlankString
    role: NonBlankString


class OutlineSpec(BaseModel):
    title: NonBlankString
    slides: list[OutlineItem] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=list)
