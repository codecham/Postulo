"""Save the applications the hunt writes, and record the ones it sends."""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date

from sqlalchemy.orm import Session

from app.models import Application, TrackedApplication, User
from app.schemas.application import ApplicationContent, GeneratedApplication
from app.schemas.tracking import TrackingCreate, TrackingUpdate
from app.services import tracking as tracking_service
from app.services.applications import applications


@dataclass(frozen=True)
class ContactDetails:
    """What the profile does not hold but the documents show: from the hunt settings."""

    phone: str | None = None
    links: Sequence[str] = field(default=())


def save_application(
    db: Session,
    user: User,
    match_id: uuid.UUID,
    generated: GeneratedApplication,
    details: ContactDetails,
) -> Application:
    """Save an application written by the hunt, with the full contact header."""
    application = applications.create_from_claude_code(db, user, match_id, generated)
    content = ApplicationContent.model_validate(application.content)
    return applications.update_application(db, application, with_details(content, details))


def with_details(content: ApplicationContent, details: ContactDetails) -> ApplicationContent:
    """Fill the phone and the links when the header has none."""
    contact = content.contact.model_copy(
        update={
            "phone": content.contact.phone or details.phone,
            "links": content.contact.links or list(details.links),
        }
    )
    return content.model_copy(update={"contact": contact})


def mark_sent(
    db: Session, user_id: uuid.UUID, match_id: uuid.UUID, notes: str | None, today: date
) -> TrackedApplication:
    """Move the match to the tracking board, with a reminder to follow up in a week."""
    tracking = tracking_service.start_tracking(db, user_id, match_id, TrackingCreate(), today)
    if notes:
        tracking = tracking_service.update_tracking(db, tracking, TrackingUpdate(notes=notes))
    return tracking
