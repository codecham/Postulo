"""Builders shared by the job search tests."""

from typing import Any

from sqlalchemy.orm import Session

from app.models import JobOffer, Profile, User
from app.services import profiles
from app.services.job_search.criteria import SearchCriteria


def create_user(db: Session, email: str = "alice@mail.com", **profile_fields: Any) -> User:
    """A saved user whose profile has the given fields (a searchable profile by default)."""
    user = User(email=email, hashed_password="not a real hash")
    db.add(user)
    db.commit()
    profile = profiles.get_or_create_profile(db, user.id)
    fields = {"desired_titles": ["Python developer"], "skills": ["Python", "FastAPI"]}
    for field, value in (fields | profile_fields).items():
        setattr(profile, field, value)
    db.commit()
    return user


def make_criteria(**changes: Any) -> SearchCriteria:
    fields: dict[str, Any] = {
        "keywords": ("Python developer",),
        "skills": ("Python", "FastAPI"),
        "countries": ("BE",),
        "work_modes": (),
        "open_to_remote_abroad": True,
        "offer_languages": ("fr", "en"),
    }
    return SearchCriteria(**(fields | changes))


def make_offer(**changes: Any) -> JobOffer:
    """An unsaved offer, for the functions that only read its attributes."""
    fields: dict[str, Any] = {
        "source": "fake",
        "external_id": "1",
        "url": "https://jobs.example.com/1",
        "title": "Python developer",
        "description": "Build our API.",
        "location": None,
        "country": "BE",
        "work_mode": "onsite",
        "language": "en",
        "tags": [],
    }
    return JobOffer(**(fields | changes))


def profile_of(db: Session, user: User) -> Profile:
    return profiles.get_or_create_profile(db, user.id)
