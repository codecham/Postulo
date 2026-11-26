"""Turn the offers Claude read in the browser into offers the search can save."""

from app.schemas.hunt import BrowserFindings, BrowserOffer
from app.services.job_search.offer import CollectedOffer


def to_collected_offers(findings: BrowserFindings) -> list[CollectedOffer]:
    return [to_collected_offer(offer) for offer in findings.offers]


def to_collected_offer(offer: BrowserOffer) -> CollectedOffer:
    return CollectedOffer(
        source=offer.board,
        external_id=offer.external_id or offer.url,
        url=offer.url,
        title=offer.title,
        description=offer.description,
        company=offer.company,
        location=offer.location,
        country=offer.country,
        work_mode=offer.work_mode,
        salary=offer.salary,
        published_at=offer.published_at,
    )
