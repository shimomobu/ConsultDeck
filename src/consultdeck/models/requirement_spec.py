from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

NonBlankString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class RequirementSpec(BaseModel):
    theme: NonBlankString
    purpose: NonBlankString
    audience: NonBlankString
    slide_count: int = Field(ge=1)
    constraints: str | None = None
    tone: NonBlankString = "formal"
    template_id: str | None = None
