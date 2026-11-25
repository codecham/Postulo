import uuid
from datetime import date
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from app.schemas.fields import MediumText, OptionalLongText, OptionalShortText


class ExperienceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: MediumText
    company: MediumText
    location: OptionalShortText = None
    start_date: date
    end_date: date | None = None  # None: the user still holds this job
    description: OptionalLongText = None

    @model_validator(mode="after")
    def check_end_date_after_start_date(self) -> Self:
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class ExperienceUpdate(ExperienceCreate):
    """Same fields as ExperienceCreate: PUT replaces the whole experience."""


class ExperienceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    company: str
    location: str | None
    start_date: date
    end_date: date | None
    description: str | None
