from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from sqlalchemy.orm import Session

from app.models import JobMatch, MatchStatus, User
from app.schemas.job_match import MatchQuery, MatchSort
from app.services.job_search import dashboard
from app.services.job_search.errors import MatchNotFoundError
from tests.services.job_search.helpers import add_match, create_user


def listed(db: Session, user: User, **query: Any) -> list[JobMatch]:
    matches, _ = dashboard.list_matches(db, user.id, MatchQuery(**query))
    return list(matches)


def test_matches_come_best_score_first(db: Session) -> None:
    user = create_user(db)
    low = add_match(db, user, score=40)
    high = add_match(db, user, score=90)

    assert listed(db, user) == [high, low]


def test_sort_by_date_puts_the_newest_offer_first(db: Session) -> None:
    user = create_user(db)
    now = datetime.now(UTC)
    old = add_match(db, user, score=90, published_at=now - timedelta(days=5))
    recent = add_match(db, user, score=40, published_at=now)

    assert listed(db, user, sort=MatchSort.DATE) == [recent, old]


def test_only_the_matches_of_the_asked_status_are_listed(db: Session) -> None:
    user = create_user(db)
    add_match(db, user, status=MatchStatus.NEW)
    saved = add_match(db, user, status=MatchStatus.SAVED)

    assert listed(db, user, status=MatchStatus.SAVED) == [saved]


@pytest.mark.parametrize(
    ("query", "offer"),
    [
        ({"min_score": 60}, {}),
        ({"work_mode": ["remote"]}, {"work_mode": "remote"}),
        ({"work_mode": ["onsite"]}, {"work_mode": None}),
        ({"country": ["FR"]}, {"country": "FR"}),
        ({"language": ["fr"]}, {"language": "fr"}),
        ({"source": ["jobicy"]}, {"source": "jobicy"}),
    ],
)
def test_filters_keep_the_matching_offers(
    db: Session, query: dict[str, Any], offer: dict[str, Any]
) -> None:
    user = create_user(db)
    add_match(db, user, score=50, country="BE", language="en", work_mode="hybrid")
    wanted = add_match(db, user, score=70, **offer)

    assert listed(db, user, **query) == [wanted]


def test_max_age_uses_the_publication_date(db: Session) -> None:
    user = create_user(db)
    add_match(db, user, published_at=datetime.now(UTC) - timedelta(days=10))
    recent = add_match(db, user, published_at=datetime.now(UTC) - timedelta(days=1))

    assert listed(db, user, max_age_days=3) == [recent]


def test_pages_split_the_matches_and_give_the_total(db: Session) -> None:
    user = create_user(db)
    best, middle, _ = (add_match(db, user, score=score) for score in (90, 60, 30))

    matches, total = dashboard.list_matches(db, user.id, MatchQuery(limit=2))
    next_page, _ = dashboard.list_matches(db, user.id, MatchQuery(limit=2, offset=2))

    assert list(matches) == [best, middle]
    assert len(next_page) == 1
    assert total == 3


def test_count_by_status_applies_the_filters(db: Session) -> None:
    user = create_user(db)
    add_match(db, user, score=80, status=MatchStatus.SAVED)
    add_match(db, user, score=80)
    add_match(db, user, score=20)

    counts = dashboard.count_by_status(db, user.id, MatchQuery(min_score=50))

    assert counts == {MatchStatus.NEW: 1, MatchStatus.SAVED: 1, MatchStatus.DISMISSED: 0}


def test_facets_list_the_values_found_in_the_matches(db: Session) -> None:
    user = create_user(db)
    add_match(db, user, source="remotive", country="FR", language="fr")
    add_match(db, user, source="jobicy", country=None, language="en")

    facets = dashboard.match_facets(db, user.id)

    assert facets.sources == ["jobicy", "remotive"]
    assert facets.countries == ["FR"]
    assert facets.languages == ["en", "fr"]


def test_set_status_saves_the_match(db: Session) -> None:
    user = create_user(db)
    match = add_match(db, user)

    updated = dashboard.set_status(db, user.id, match.id, MatchStatus.SAVED)

    assert updated.status == MatchStatus.SAVED


def test_users_cannot_change_the_matches_of_others(db: Session) -> None:
    alice = create_user(db, "alice@mail.com")
    bob = create_user(db, "bob@mail.com")
    match = add_match(db, alice)

    with pytest.raises(MatchNotFoundError):
        dashboard.set_status(db, bob.id, match.id, MatchStatus.DISMISSED)
