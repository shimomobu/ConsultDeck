from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

NonBlankString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class TemplateSpec(BaseModel):
    template_id: NonBlankString
    name: NonBlankString
    doc_type: NonBlankString
    use_case: NonBlankString
    audience: NonBlankString
    phase: NonBlankString
    slide_structure: list[NonBlankString] = Field(min_length=1)
