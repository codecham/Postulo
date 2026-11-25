"""A tailored application: the CV and the cover letter written for one job offer.

`GeneratedApplication` is the contract with the AI (the paid API and the free Claude Code
command both produce it). `ApplicationContent` is what is stored and edited: the same
documents plus the language and the contact details, which never come from the AI.
"""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.schemas.fields import (
    LongText,
    MediumText,
    OptionalLongText,
    OptionalMediumText,
    OptionalShortText,
    ShortText,
    TagList,
)

# A month as YYYY-MM, such as "2024-06"
YearMonth = Annotated[
    str, StringConstraints(strip_whitespace=True, pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
]

MAX_BULLETS = 8
MAX_EXPERIENCES = 15
MAX_EDUCATIONS = 10
MAX_PARAGRAPHS = 6
MAX_LINKS = 5


class ApplicationLanguage(StrEnum):
    """The languages the documents can be written in (labels, dates, AI wording)."""

    FR = "fr"
    EN = "en"


class CvExperience(BaseModel):
    title: MediumText = Field(description="Job title, as in the candidate's profile")
    company: MediumText
    location: OptionalShortText = Field(description="City and/or country, or null")
    start_month: YearMonth | None = Field(description="YYYY-MM, as in the profile, or null")
    end_month: YearMonth | None = Field(description="YYYY-MM, or null for a current job")
    bullets: list[LongText] = Field(
        max_length=MAX_BULLETS,
        description="2 to 5 achievements or responsibilities, the most relevant to the "
        "offer first, each one sentence starting with a verb",
    )


class CvEducation(BaseModel):
    school: MediumText
    degree: OptionalMediumText = Field(description="Degree or diploma, or null")
    field_of_study: OptionalMediumText
    location: OptionalShortText
    start_month: YearMonth | None
    end_month: YearMonth | None
    details: OptionalLongText = Field(description="One short line, only if relevant, or null")


class TailoredCv(BaseModel):
    headline: MediumText = Field(description="Professional title aimed at the offer")
    summary: LongText = Field(
        description="3 or 4 sentences: who the candidate is and why they fit this offer"
    )
    skills: TagList = Field(
        description="The candidate's skills, those the offer asks for first; at most 15"
    )
    experiences: list[CvExperience] = Field(
        max_length=MAX_EXPERIENCES, description="Every experience of the profile, newest first"
    )
    education: list[CvEducation] = Field(
        max_length=MAX_EDUCATIONS, description="Every education of the profile, newest first"
    )
    languages: list[ShortText] = Field(
        max_length=10,
        description="Spoken languages written out in the document language, such as "
        "'English' or 'Français'",
    )


class CoverLetter(BaseModel):
    subject: MediumText = Field(description="Subject line naming the job title")
    greeting: ShortText = Field(description="Such as 'Dear Hiring Manager,' or 'Madame, Monsieur,'")
    paragraphs: list[LongText] = Field(
        min_length=1,
        max_length=MAX_PARAGRAPHS,
        description="3 or 4 short paragraphs: the hook, the fit with concrete proof from the "
        "profile, the motivation for this company, the call to action",
    )
    closing: MediumText = Field(description="Closing formula, without the signature")


class GeneratedApplication(BaseModel):
    """What the AI writes for one offer."""

    cv: TailoredCv
    cover_letter: CoverLetter


class Contact(BaseModel):
    """The header of both documents, filled from the profile and editable."""

    full_name: OptionalMediumText = None
    email: OptionalMediumText = None
    phone: OptionalShortText = None
    city: OptionalShortText = None
    links: list[MediumText] = Field(default=[], max_length=MAX_LINKS)


class ApplicationContent(GeneratedApplication):
    """The documents as stored and edited. Body of PUT .../application."""

    model_config = ConfigDict(extra="forbid")

    language: ApplicationLanguage
    contact: Contact


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    match_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    # Who wrote it: an API model id, or "claude-code"
    model: str
    content: ApplicationContent


class ApplicationOptions(BaseModel):
    """Which ways to write an application this server offers."""

    # False without ANTHROPIC_API_KEY: only the Claude Code command works then
    ai_generation: bool
