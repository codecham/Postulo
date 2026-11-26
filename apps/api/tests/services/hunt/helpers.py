"""Builders shared by the hunt tests."""

from typing import Any

from sqlalchemy.orm import Session

from app.models import Application, JobMatch, User
from app.schemas.hunt import BrowserOffer
from app.services.hunt import applying
from tests.fakes import make_generated_application

DESCRIPTION = "We are looking for a Python developer to build our API with FastAPI. " * 3


def make_browser_offer(**changes: Any) -> BrowserOffer:
    fields: dict[str, Any] = {
        "board": "linkedin",
        "external_id": "4012345678",
        "url": "https://www.linkedin.com/jobs/view/4012345678",
        "title": "Python backend developer",
        "company": "Acme",
        "location": "Brussels",
        "country": "BE",
        "work_mode": "hybrid",
        "description": DESCRIPTION,
    }
    return BrowserOffer.model_validate(fields | changes)


def write_application(db: Session, user: User, match: JobMatch) -> Application:
    return applying.save_application(
        db, user, match.id, make_generated_application(), applying.ContactDetails()
    )
