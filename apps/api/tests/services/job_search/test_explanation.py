from app.models import JobMatch
from app.schemas.job_match import MatchPlace
from app.services.job_search.explanation import explain, place_of
from tests.services.job_search.helpers import make_criteria, make_offer


def test_an_offer_in_a_wanted_country_is_placed_there() -> None:
    offer = make_offer(country="BE", work_mode="remote")

    assert place_of(offer, make_criteria(countries=("BE",))) == MatchPlace.YOUR_COUNTRY


def test_a_remote_offer_abroad_is_remote() -> None:
    offer = make_offer(country=None, work_mode="remote")

    assert place_of(offer, make_criteria(countries=("BE",))) == MatchPlace.REMOTE


def test_an_offer_outside_the_current_criteria_is_other() -> None:
    offer = make_offer(country="FR", work_mode="onsite")

    assert place_of(offer, make_criteria(countries=("BE",))) == MatchPlace.OTHER


def test_explain_gives_the_relevance_and_the_matched_skills() -> None:
    match = JobMatch(offer=make_offer(), similarity=0.6, matched_skills=["Python"], score=70)

    explanation = explain(match, make_criteria())

    assert explanation.relevance == 50
    assert explanation.matched_skills == ["Python"]
