from app.services.job_search.filters import fits_criteria
from tests.services.job_search.helpers import make_criteria, make_offer


def test_an_onsite_offer_in_a_wanted_country_fits() -> None:
    assert fits_criteria(make_offer(country="BE", work_mode="onsite"), make_criteria())


def test_an_onsite_offer_in_another_country_does_not_fit() -> None:
    assert not fits_criteria(make_offer(country="FR", work_mode="onsite"), make_criteria())


def test_an_offer_with_an_unwanted_work_mode_does_not_fit() -> None:
    criteria = make_criteria(work_modes=("remote",))

    assert not fits_criteria(make_offer(work_mode="hybrid"), criteria)


def test_a_remote_offer_abroad_fits_when_its_region_includes_the_user() -> None:
    offer = make_offer(country=None, work_mode="remote", location="Europe")

    assert fits_criteria(offer, make_criteria(open_to_remote_abroad=True))
    assert not fits_criteria(offer, make_criteria(open_to_remote_abroad=False))


def test_an_offer_in_an_unwanted_language_does_not_fit() -> None:
    assert not fits_criteria(make_offer(language="de"), make_criteria())


def test_an_offer_whose_language_is_unknown_fits() -> None:
    assert fits_criteria(make_offer(language=None), make_criteria())


def test_no_language_criterion_accepts_every_language() -> None:
    assert fits_criteria(make_offer(language="de"), make_criteria(offer_languages=()))
