from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models import MatchStatus
from app.services.hunt import applying, selection
from tests.services.hunt.helpers import write_application
from tests.services.job_search.helpers import add_match, create_user

TODAY = datetime.now(UTC).date()


def test_candidates_are_the_best_new_matches(db: Session) -> None:
    user = create_user(db)
    low = add_match(db, user, score=40)
    high = add_match(db, user, score=80)
    add_match(db, user, score=90, status=MatchStatus.DISMISSED)

    assert selection.list_candidates(db, user.id, limit=5) == [high, low]
    assert selection.list_candidates(db, user.id, limit=1) == [high]


def test_candidates_skip_old_offers_and_written_applications(db: Session) -> None:
    user = create_user(db)
    old = datetime.now(UTC) - selection.CANDIDATE_MAX_AGE - timedelta(days=1)
    add_match(db, user, published_at=old)
    written = add_match(db, user)
    write_application(db, user, written)
    fresh = add_match(db, user)

    assert selection.list_candidates(db, user.id, limit=5) == [fresh]


def test_ready_lists_written_applications_not_sent_yet(db: Session) -> None:
    user = create_user(db)
    first, second, sent = (add_match(db, user) for _ in range(3))
    for match in (first, second, sent):
        write_application(db, user, match)
    applying.mark_sent(db, user.id, sent.id, notes=None, today=TODAY)
    add_match(db, user)  # no application

    assert selection.list_ready(db, user.id) == [first, second]


def test_ready_skips_the_applications_the_user_dismissed(db: Session) -> None:
    user = create_user(db)
    match = add_match(db, user)
    write_application(db, user, match)
    match.status = MatchStatus.DISMISSED
    db.commit()

    assert selection.list_ready(db, user.id) == []


def test_matches_of_other_users_are_never_listed(db: Session) -> None:
    alice, bob = create_user(db), create_user(db, email="bob@mail.com")
    write_application(db, bob, add_match(db, bob))
    add_match(db, bob)

    assert selection.list_candidates(db, alice.id, limit=5) == []
    assert selection.list_ready(db, alice.id) == []
