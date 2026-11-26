"""The daily hunt: offers found by browsing job boards in Chrome (Claude in Chrome)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.profile import WorkMode


class BrowserOffer(BaseModel):
    """A job offer read on a job board's page, as Claude writes it in the findings file."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    # Short name of the job board, e.g. "linkedin" or "welcometothejungle"
    board: str = Field(min_length=2, max_length=40, pattern=r"^[a-z0-9-]+$")
    # The board's own id of the offer; None: the offer's URL identifies it
    external_id: str | None = Field(default=None, max_length=200)
    url: str = Field(min_length=8, max_length=2000, pattern=r"^https?://")
    title: str = Field(min_length=2, max_length=300)
    company: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=300)
    country: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")  # ISO 3166-1 alpha-2
    work_mode: WorkMode | None = None
    # The full text of the offer: what it is scored and tailored against
    description: str = Field(min_length=100)
    salary: str | None = Field(default=None, max_length=100)
    published_at: datetime | None = None


class BrowserFindings(BaseModel):
    """The findings file: every offer collected in one browsing session."""

    model_config = ConfigDict(extra="forbid")

    offers: list[BrowserOffer] = Field(max_length=200)
