"""Tracking of sent applications: their status, dates, notes and history."""

import uuid
from datetime import date, datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from app.models import TrackingStatus
from app.schemas.fields import OptionalLongText, ensure_end_after_start
from app.schemas.job_search import JobOfferRead


class TrackingCreate(BaseModel):
    """Body of POST .../tracking ("Mark as sent"). Every field has a default."""

    model_config = ConfigDict(extra="forbid")

    applied_on: date | None = None  # None: today
    follow_up_on: date | None = None  # None: a week after applied_on

    @model_validator(mode="after")
    def follow_up_after_applying(self) -> Self:
        ensure_end_after_start(self.applied_on, self.follow_up_on)
        return self


class TrackingUpdate(BaseModel):
    """Body of PATCH .../tracking: only the fields sent are changed."""

    model_config = ConfigDict(extra="forbid")

    status: TrackingStatus | None = None
    applied_on: date | None = None
    follow_up_on: date | None = None  # null removes the reminder
    notes: OptionalLongText = None

    @model_validator(mode="after")
    def no_null_status_or_date(self) -> Self:
        for field in ("status", "applied_on"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class TrackingEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: TrackingStatus
    created_at: datetime


class TrackingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    match_id: uuid.UUID
    status: TrackingStatus
    applied_on: date
    follow_up_on: date | None
    notes: str | None
    # True when the follow-up date has come and the user still waits for an answer
    follow_up_due: bool
    events: list[TrackingEventRead]


class TrackedApplicationRead(TrackingRead):
    """A tracked application with its offer, for the tracking board."""

    offer: JobOfferRead


class TrackingCounts(BaseModel):
    applied: int
    interview: int
    offer: int
    rejected: int
    withdrawn: int


class TrackingBoard(BaseModel):
    items: list[TrackedApplicationRead]
    counts: TrackingCounts
