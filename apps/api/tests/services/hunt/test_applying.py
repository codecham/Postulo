from datetime import date, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models import MatchStatus, TrackingStatus
from app.schemas.application import ApplicationContent
from app.services.hunt import applying
from app.services.tracking import AlreadyTrackedError
from tests.fakes import make_generated_application
from tests.services.hunt.helpers import write_application
from tests.services.job_search.helpers import add_match, create_user

TODAY = date(2026, 11, 26)
DETAILS = applying.ContactDetails(phone="+32 470 00 00 00", links=["github.com/alice"])


def test_the_application_gets_the_phone_and_links_of_the_settings(db: Session) -> None:
    user = create_user(db)
    match = add_match(db, user)

    application = applying.save_application(
        db, user, match.id, make_generated_application(), DETAILS
    )

    contact = ApplicationContent.model_validate(application.content).contact
    assert (contact.phone, contact.links) == ("+32 470 00 00 00", ["github.com/alice"])
    assert contact.email == user.email
    assert match.status == MatchStatus.SAVED


def test_details_never_replace_what_the_header_has() -> None:
    content = ApplicationContent.model_validate(
        {
            **make_generated_application().model_dump(),
            "language": "en",
            "contact": {"phone": "0470", "links": ["mysite.dev"]},
        }
    )

    contact = applying.with_details(content, DETAILS).contact

    assert (contact.phone, contact.links) == ("0470", ["mysite.dev"])


def test_mark_sent_tracks_the_application_with_notes(db: Session) -> None:
    user = create_user(db)
    match = add_match(db, user)
    write_application(db, user, match)

    tracking = applying.mark_sent(db, user.id, match.id, notes="Greenhouse form", today=TODAY)

    assert tracking.status == TrackingStatus.APPLIED
    assert tracking.applied_on == TODAY
    assert tracking.follow_up_on == TODAY + timedelta(days=7)
    assert tracking.notes == "Greenhouse form"


def test_an_application_is_marked_sent_once(db: Session) -> None:
    user = create_user(db)
    match = add_match(db, user)
    applying.mark_sent(db, user.id, match.id, notes=None, today=TODAY)

    with pytest.raises(AlreadyTrackedError):
        applying.mark_sent(db, user.id, match.id, notes=None, today=TODAY)
