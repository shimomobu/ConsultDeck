from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

NonBlankString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Section(BaseModel):
    section_title: NonBlankString
    slide_titles: list[NonBlankString] = Field(default_factory=list)


class OutlineSpec(BaseModel):
    title: NonBlankString
    sections: list[Section] = Field(default_factory=list)
