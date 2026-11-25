"""The matches dashboard: ranked offers, their filters, and what the user did with them."""

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.models import MatchStatus
from app.schemas.job_search import JobOfferRead
from app.schemas.profile import CountryCode, LanguageCode, WorkMode


class MatchSort(StrEnum):
    SCORE = "score"  # best fit first
    DATE = "date"  # newest offer first


class MatchPlace(StrEnum):
    """Why the offer's place suits the user."""

    YOUR_COUNTRY = "your_country"  # in one of the countries the user wants
    REMOTE = "remote"  # remote, open to where the user lives
    OTHER = "other"  # the criteria changed since the last search


class MatchQuery(BaseModel):
    """Query parameters of GET /job-search/matches. Empty lists mean "any"."""

    model_config = ConfigDict(extra="forbid")

    status: MatchStatus = MatchStatus.NEW
    min_score: int = Field(default=0, ge=0, le=100)
    work_mode: list[WorkMode] = []
    country: list[CountryCode] = []
    language: list[LanguageCode] = []
    source: list[str] = []
    # Only offers published (or found) in the last N days
    max_age_days: int | None = Field(default=None, ge=1, le=365)
    sort: MatchSort = MatchSort.SCORE
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class MatchExplanation(BaseModel):
    """Why the offer was matched, in a few facts the page turns into sentences."""

    model_config = ConfigDict(from_attributes=True)

    # The meaning part of the score, 0 to 100: how close the offer is to the profile
    relevance: int
    # The profile's skills that the offer names
    matched_skills: list[str]
    place: MatchPlace


class JobMatchRead(BaseModel):
    id: uuid.UUID
    score: int
    status: MatchStatus
    created_at: datetime
    offer: JobOfferRead
    explanation: MatchExplanation


class MatchStatusCounts(BaseModel):
    new: int
    saved: int
    dismissed: int


class JobMatchPage(BaseModel):
    items: list[JobMatchRead]
    # Matches with this status that pass the filters, for the pagination
    total: int
    # Matches of each status that pass the filters, for the tabs
    counts: MatchStatusCounts


class MatchFacets(BaseModel):
    """The values found in the user's matches, to offer as filters."""

    sources: list[str]
    countries: list[str]
    languages: list[str]


class JobMatchUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: MatchStatus
