"""Combine the data found in a CV with what the user already saved.

Rule: the CV wins for single values it provides, lists are combined, and nothing the
user already has is lost.
"""

from collections.abc import Sequence
from datetime import date

from app.models import Experience, Profile
from app.schemas.cv_import import DraftExperience
from app.schemas.experience import ExperienceCreate
from app.schemas.fields import TAG_LIST_MAX_LENGTH, unique_ignoring_case
from app.schemas.profile import ProfileUpdate


def merge_profile(current: Profile, extracted: ProfileUpdate) -> ProfileUpdate:
    return ProfileUpdate(
        full_name=extracted.full_name or current.full_name,
        headline=extracted.headline or current.headline,
        summary=extracted.summary or current.summary,
        city=extracted.city or current.city,
        skills=combine(current.skills, extracted.skills),
        languages=combine(current.languages, extracted.languages),
        desired_titles=combine(current.desired_titles, extracted.desired_titles),
        work_modes=combine(current.work_modes, extracted.work_modes),
        countries=combine(current.countries, extracted.countries),
        open_to_remote_abroad=current.open_to_remote_abroad or extracted.open_to_remote_abroad,
    )


def combine(current: Sequence[str], extracted: Sequence[str]) -> list[str]:
    """Current values first, then the new ones, without duplicates, within the list limit."""
    return unique_ignoring_case([*current, *extracted])[:TAG_LIST_MAX_LENGTH]


def mark_known_experiences(
    current: Sequence[Experience], extracted: Sequence[ExperienceCreate]
) -> list[DraftExperience]:
    known_keys = {_experience_key(item.title, item.company, item.start_date) for item in current}
    return [
        DraftExperience(
            **item.model_dump(),
            already_exists=_experience_key(item.title, item.company, item.start_date) in known_keys,
        )
        for item in extracted
    ]


def _experience_key(title: str, company: str, start_date: date) -> tuple[str, str, int, int]:
    """Two experiences are the same job if title, company and start month match."""
    return (title.casefold(), company.casefold(), start_date.year, start_date.month)
