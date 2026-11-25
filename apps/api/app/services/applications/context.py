"""What the AI needs to write an application: the candidate, the offer and the language."""

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

from app.models import Education, Experience, JobOffer, Profile
from app.schemas.application import ApplicationLanguage

# Long offers are cut: the start says what the job is, the rest is often boilerplate
MAX_OFFER_DESCRIPTION_LENGTH = 12000


@dataclass(frozen=True)
class ApplicationContext:
    language: ApplicationLanguage
    candidate: dict[str, Any]
    offer: dict[str, Any]

    def as_prompt(self) -> str:
        """The facts given to the AI, as one message."""
        return (
            f"Document language: {self.language.value}\n\n"
            f"Candidate profile (JSON):\n{_to_json(self.candidate)}\n\n"
            f"Job offer (JSON):\n{_to_json(self.offer)}"
        )


def document_language(offer: JobOffer) -> ApplicationLanguage:
    """Write in the offer's language; English when it is unknown or not supported."""
    try:
        return ApplicationLanguage(offer.language or "")
    except ValueError:
        return ApplicationLanguage.EN


def build_context(
    profile: Profile,
    experiences: Sequence[Experience],
    educations: Sequence[Education],
    offer: JobOffer,
) -> ApplicationContext:
    return ApplicationContext(
        language=document_language(offer),
        candidate=describe_candidate(profile, experiences, educations),
        offer=describe_offer(offer),
    )


def describe_candidate(
    profile: Profile, experiences: Sequence[Experience], educations: Sequence[Education]
) -> dict[str, Any]:
    return {
        "full_name": profile.full_name,
        "headline": profile.headline,
        "summary": profile.summary,
        "city": profile.city,
        "skills": profile.skills,
        "spoken_languages": profile.languages,
        "experiences": [_describe_experience(item) for item in experiences],
        "education": [_describe_education(item) for item in educations],
    }


def describe_offer(offer: JobOffer) -> dict[str, Any]:
    return {
        "title": offer.title,
        "company": offer.company,
        "location": offer.location,
        "work_mode": offer.work_mode,
        "tags": offer.tags,
        "description": offer.description[:MAX_OFFER_DESCRIPTION_LENGTH],
    }


def _describe_experience(experience: Experience) -> dict[str, Any]:
    return {
        "title": experience.title,
        "company": experience.company,
        "location": experience.location,
        "start_month": _month(experience.start_date),
        "end_month": _month(experience.end_date),
        "is_current": experience.end_date is None,
        "description": experience.description,
    }


def _describe_education(education: Education) -> dict[str, Any]:
    return {
        "school": education.school,
        "degree": education.degree,
        "field_of_study": education.field_of_study,
        "location": education.location,
        "start_month": _month(education.start_date),
        "end_month": _month(education.end_date),
        "description": education.description,
    }


def _month(value: date | None) -> str | None:
    return value.strftime("%Y-%m") if value else None


def _to_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
