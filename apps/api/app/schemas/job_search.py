import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import JobSearchRunStatus, JobSearchTrigger
from app.schemas.profile import WorkMode


class JobSearchRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: JobSearchRunStatus
    trigger: JobSearchTrigger
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    offers_found: int
    offers_new: int
    matches_found: int
    failed_sources: list[str]
    error: str | None


class JobSourceRead(BaseModel):
    """A job board, and whether this server collects its offers."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    url: str
    enabled: bool


class JobSearchOverview(BaseModel):
    latest_run: JobSearchRunRead | None
    sources: list[JobSourceRead]


class JobOfferRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source: str
    url: str
    title: str
    company: str | None
    location: str | None
    country: str | None
    work_mode: WorkMode | None
    language: str | None
    description: str
    tags: list[str]
    salary: str | None
    published_at: datetime | None


class JobMatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    score: int
    matched_skills: list[str]
    created_at: datetime
    offer: JobOfferRead
