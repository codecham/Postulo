import pytest
from pydantic import ValidationError

from app.schemas.hunt import BrowserFindings
from app.services.hunt.findings import to_collected_offer, to_collected_offers
from tests.services.hunt.helpers import make_browser_offer


def test_a_browser_offer_keeps_its_board_and_id() -> None:
    offer = to_collected_offer(make_browser_offer())

    assert offer.key == ("linkedin", "4012345678")
    assert (offer.company, offer.country, offer.work_mode) == ("Acme", "BE", "hybrid")


def test_the_url_identifies_an_offer_without_id() -> None:
    offer = to_collected_offer(make_browser_offer(external_id=None))

    assert offer.external_id == "https://www.linkedin.com/jobs/view/4012345678"


def test_findings_turn_into_collected_offers() -> None:
    findings = BrowserFindings(offers=[make_browser_offer(), make_browser_offer(board="ictjob")])

    assert [offer.source for offer in to_collected_offers(findings)] == ["linkedin", "ictjob"]


@pytest.mark.parametrize(
    "changes",
    [
        {"board": "LinkedIn"},  # board names are lowercase slugs
        {"url": "javascript:alert(1)"},
        {"description": "Too short to score."},
        {"country": "Belgium"},
        {"work_mode": "sometimes"},
    ],
)
def test_invalid_browser_offers_are_refused(changes: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        make_browser_offer(**changes)
