"""Turn what the AI extracted into data that passes the profile and experience schemas.

The AI output is not trusted: items that are invalid are dropped (with a warning when
the user may want to add them by hand), and texts that are too long are shortened.
"""

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from pydantic import TypeAdapter, ValidationError

from app.schemas.education import EducationCreate
from app.schemas.experience import ExperienceCreate
from app.schemas.fields import (
    LONG_TEXT_MAX_LENGTH,
    MEDIUM_TEXT_MAX_LENGTH,
    SHORT_TEXT_MAX_LENGTH,
    TAG_LIST_MAX_LENGTH,
    ShortText,
)
from app.schemas.profile import CountryCode, LanguageCode, ProfileUpdate
from app.services.cv_import.extraction import (
    CvExtraction,
    ExtractedEducation,
    ExtractedExperience,
)

MONTH_PATTERN = re.compile(r"^(\d{4})-(\d{2})$")


@dataclass
class NormalizedCv:
    profile: ProfileUpdate
    experiences: list[ExperienceCreate]
    educations: list[EducationCreate]
    warnings: list[str] = field(default_factory=list)


def normalize_extraction(extraction: CvExtraction) -> NormalizedCv:
    warnings: list[str] = []
    experiences = [
        experience
        for item in extraction.experiences
        if (experience := normalize_experience(item, warnings)) is not None
    ]
    educations = [
        education
        for item in extraction.education
        if (education := normalize_education(item, warnings)) is not None
    ]
    return NormalizedCv(normalize_profile(extraction), experiences, educations, warnings)


def normalize_profile(extraction: CvExtraction) -> ProfileUpdate:
    return ProfileUpdate(
        full_name=shorten(extraction.full_name, MEDIUM_TEXT_MAX_LENGTH),
        headline=shorten(extraction.headline, MEDIUM_TEXT_MAX_LENGTH),
        summary=shorten(extraction.summary, LONG_TEXT_MAX_LENGTH),
        city=shorten(extraction.city, SHORT_TEXT_MAX_LENGTH),
        skills=keep_valid(extraction.skills, ShortText),
        languages=keep_valid(extraction.languages, LanguageCode),
        desired_titles=keep_valid(extraction.desired_titles, ShortText),
        work_modes=extraction.work_modes,
        countries=keep_valid(extraction.countries, CountryCode),
        open_to_remote_abroad=extraction.open_to_remote_abroad,
    )


def normalize_experience(item: ExtractedExperience, warnings: list[str]) -> ExperienceCreate | None:
    """A valid experience, or None (and a warning) when it cannot be saved as is."""
    label = f"{item.title} at {item.company}"
    start_date = parse_month(item.start_month)
    if start_date is None:
        warnings.append(f"{label}: skipped, the start date is missing.")
        return None
    end_date = None if item.is_current else parse_month(item.end_month)
    if end_date is not None and end_date < start_date:
        warnings.append(f"{label}: the end date was before the start date, it was removed.")
        end_date = None
    try:
        return ExperienceCreate(
            title=shorten(item.title, MEDIUM_TEXT_MAX_LENGTH),
            company=shorten(item.company, MEDIUM_TEXT_MAX_LENGTH),
            location=shorten(item.location, SHORT_TEXT_MAX_LENGTH),
            start_date=start_date,
            end_date=end_date,
            description=shorten(item.description, LONG_TEXT_MAX_LENGTH),
        )
    except ValidationError:
        warnings.append(f"{label}: skipped, the title or the company is missing.")
        return None


def normalize_education(item: ExtractedEducation, warnings: list[str]) -> EducationCreate | None:
    """A valid education, or None (and a warning) when it cannot be saved as is."""
    start_date = parse_month(item.start_month)
    end_date = parse_month(item.end_month)
    if start_date is not None and end_date is not None and end_date < start_date:
        warnings.append(f"{item.school}: the end date was before the start date, it was removed.")
        end_date = None
    try:
        return EducationCreate(
            school=shorten(item.school, MEDIUM_TEXT_MAX_LENGTH),
            degree=shorten(item.degree, MEDIUM_TEXT_MAX_LENGTH),
            field_of_study=shorten(item.field_of_study, MEDIUM_TEXT_MAX_LENGTH),
            location=shorten(item.location, SHORT_TEXT_MAX_LENGTH),
            start_date=start_date,
            end_date=end_date,
            description=shorten(item.description, LONG_TEXT_MAX_LENGTH),
        )
    except ValidationError:
        warnings.append("An education without a school name was skipped.")
        return None


def parse_month(value: str | None) -> date | None:
    """'2024-03' -> date(2024, 3, 1); None for a missing or invalid month."""
    match = MONTH_PATTERN.match(value.strip()) if value else None
    if match is None:
        return None
    year, month = int(match[1]), int(match[2])
    return date(year, month, 1) if 1 <= month <= 12 else None


def shorten(value: str | None, max_length: int) -> str | None:
    """Trim the text and cut it to max_length characters (the schemas reject longer ones)."""
    if value is None:
        return None
    return value.strip()[:max_length]


def keep_valid(values: list[str], item_type: Any) -> list[str]:
    """The values that pass `item_type` validation, cleaned, at most TAG_LIST_MAX_LENGTH."""
    adapter: TypeAdapter[str] = TypeAdapter(item_type)
    valid: list[str] = []
    for value in values:
        try:
            valid.append(adapter.validate_python(value))
        except ValidationError:
            continue
    return valid[:TAG_LIST_MAX_LENGTH]
