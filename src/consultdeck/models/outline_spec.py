from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonBlankString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class OutlineItem(BaseModel):
    slide_id: NonBlankString
    title: NonBlankString
    role: NonBlankString


class OutlineSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: NonBlankString
    slides: list[OutlineItem] = Field(default_factory=list)
