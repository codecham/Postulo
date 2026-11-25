"""What the AI must return for a CV, and the interface of anything that extracts it.

CvExtraction is the contract with the model: plain, loosely constrained fields that are
easy to fill. `normalize` then validates them with the strict profile schemas.
"""

from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel, Field

from app.schemas.profile import WorkMode


class ExtractedExperience(BaseModel):
    title: str = Field(description="Job title, as written in the CV")
    company: str
    location: str | None = Field(description="City and/or country of the job")
    start_month: str | None = Field(description="Start month as YYYY-MM, or null if unknown")
    end_month: str | None = Field(
        description="End month as YYYY-MM, or null for a current job or an unknown date"
    )
    is_current: bool = Field(description="True if the person still holds this job")
    description: str | None = Field(description="Responsibilities and achievements")


class CvExtraction(BaseModel):
    is_cv: bool = Field(
        description="False if the document is not a CV, a resume or a professional profile"
    )
    full_name: str | None
    headline: str | None = Field(description="Short professional title, such as the CV title")
    summary: str | None = Field(description="Profile or 'about' section, in the CV language")
    city: str | None = Field(description="City where the person lives")
    skills: list[str] = Field(description="Professional skills, tools and technologies")
    languages: list[str] = Field(
        description="Spoken languages as ISO 639-1 codes, such as 'fr' or 'en'"
    )
    desired_titles: list[str] = Field(
        description="Job titles the person is looking for; if not stated, up to 3 titles "
        "close to their most recent roles"
    )
    work_modes: list[WorkMode] = Field(description="Only if the CV states a preference")
    countries: list[str] = Field(
        description="Countries where the person wants to work, as ISO 3166-1 alpha-2 codes; "
        "empty unless the CV states it"
    )
    open_to_remote_abroad: bool = Field(
        description="True only if the CV says the person accepts remote work for a foreign company"
    )
    experiences: list[ExtractedExperience] = Field(description="Work experiences, newest first")


@dataclass(frozen=True)
class ExtractionResult:
    extraction: CvExtraction
    model: str
    input_tokens: int
    output_tokens: int


class CvExtractor(Protocol):
    """Turns a PDF into a CvExtraction. Claude in production, a fake in the tests."""

    def extract(self, pdf: bytes) -> ExtractionResult:
        """Raise ExtractionFailedError when no usable answer can be produced."""
        ...
