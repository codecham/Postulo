from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models import MatchStatus
from app.services.job_search import dashboard
from app.services.job_search.matching import match_offers, nearest_offers
from app.services.job_search.offers import embed_pending_offers, save_offers
from tests.fakes import FakeEmbedder, make_collected_offer
from tests.services.job_search.helpers import create_user, make_criteria, matches_of

PROFILE_TEXT = "Python developer FastAPI PostgreSQL backend API"


def save_embedded(db: Session, *offers: object) -> None:
    save_offers(db, offers)  # type: ignore[arg-type]
    embed_pending_offers(db, FakeEmbedder())


def profile_vector() -> list[float]:
    return FakeEmbedder().embed([PROFILE_TEXT])[0]


def test_nearest_offers_come_closest_first(db: Session) -> None:
    save_embedded(
        db,
        make_collected_offer(external_id="nurse", title="Night nurse", description="Hospital"),
        make_collected_offer(external_id="python", title="Python developer FastAPI backend"),
    )

    nearest = nearest_offers(db, profile_vector(), limit=10)

    assert [offer.external_id for offer, _ in nearest] == ["python", "nurse"]
    assert nearest[0][1] > nearest[1][1]


def test_nearest_offers_skip_old_offers(db: Session) -> None:
    old = datetime.now(UTC) - timedelta(days=60)
    save_embedded(db, make_collected_offer(published_at=old))

    assert nearest_offers(db, profile_vector(), limit=10) == []


def test_match_offers_saves_the_offers_that_fit(db: Session) -> None:
    user = create_user(db)
    save_embedded(
        db,
        make_collected_offer(external_id="good", title="Python developer FastAPI backend API"),
        make_collected_offer(external_id="usa", title="Python developer", location="USA only"),
        make_collected_offer(external_id="far", title="Night nurse", description="Hospital"),
    )

    count = match_offers(db, user.id, make_criteria(), profile_vector(), min_score=40)

    matches = matches_of(db, user.id)
    assert count == 1
    assert [match.offer.external_id for match in matches] == ["good"]
    assert matches[0].matched_skills == ["Python", "FastAPI"]


def test_matching_again_updates_the_score_instead_of_duplicating(db: Session) -> None:
    user = create_user(db)
    save_embedded(db, make_collected_offer(title="Python developer FastAPI backend API"))
    match_offers(db, user.id, make_criteria(skills=()), profile_vector(), min_score=0)

    match_offers(db, user.id, make_criteria(), profile_vector(), min_score=0)

    [match] = matches_of(db, user.id)
    assert match.matched_skills == ["Python", "FastAPI"]


def test_offers_that_no_longer_fit_are_removed_from_the_matches(db: Session) -> None:
    user = create_user(db)
    save_embedded(db, make_collected_offer(title="Python developer FastAPI backend API"))
    match_offers(db, user.id, make_criteria(), profile_vector(), min_score=0)

    match_offers(db, user.id, make_criteria(offer_languages=("nl",)), profile_vector(), 0)

    assert matches_of(db, user.id) == []


def test_users_only_see_their_own_matches(db: Session) -> None:
    alice = create_user(db, "alice@mail.com")
    bob = create_user(db, "bob@mail.com")
    save_embedded(db, make_collected_offer(title="Python developer FastAPI backend API"))

    match_offers(db, alice.id, make_criteria(), profile_vector(), min_score=0)

    assert matches_of(db, bob.id) == []


def test_saved_matches_stay_when_they_no_longer_fit(db: Session) -> None:
    user = create_user(db)
    save_embedded(db, make_collected_offer(title="Python developer FastAPI backend API"))
    match_offers(db, user.id, make_criteria(), profile_vector(), min_score=0)
    [match] = matches_of(db, user.id)
    dashboard.set_status(db, user.id, match.id, MatchStatus.SAVED)

    match_offers(db, user.id, make_criteria(offer_languages=("nl",)), profile_vector(), 0)

    assert [item.id for item in matches_of(db, user.id)] == [match.id]


def test_a_new_search_keeps_the_status_of_known_matches(db: Session) -> None:
    user = create_user(db)
    save_embedded(db, make_collected_offer(title="Python developer FastAPI backend API"))
    match_offers(db, user.id, make_criteria(), profile_vector(), min_score=0)
    [match] = matches_of(db, user.id)
    dashboard.set_status(db, user.id, match.id, MatchStatus.DISMISSED)

    match_offers(db, user.id, make_criteria(), profile_vector(), min_score=0)

    [match] = matches_of(db, user.id)
    db.refresh(match)
    assert match.status == MatchStatus.DISMISSED
