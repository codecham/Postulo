import uuid
from datetime import date
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from app.schemas.fields import (
    MediumText,
    OptionalLongText,
    OptionalMediumText,
    OptionalShortText,
    ensure_end_after_start,
)


class EducationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    school: MediumText
    degree: OptionalMediumText = None
    field_of_study: OptionalMediumText = None
    location: OptionalShortText = None
    start_date: date | None = None
    end_date: date | None = None  # None with a start date: still studying there
    description: OptionalLongText = None

    @model_validator(mode="after")
    def check_end_date_after_start_date(self) -> Self:
        ensure_end_after_start(self.start_date, self.end_date)
        return self


class EducationUpdate(EducationCreate):
    """Same fields as EducationCreate: PUT replaces the whole education."""


class EducationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    school: str
    degree: str | None
    field_of_study: str | None
    location: str | None
    start_date: date | None
    end_date: date | None
    description: str | None
