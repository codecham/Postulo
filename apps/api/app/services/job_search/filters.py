"""Keep only the offers that fit the user's search criteria."""

from app.models import JobOffer
from app.services.job_search.criteria import SearchCriteria
from app.services.job_search.regions import remote_region_accepts


def fits_criteria(offer: JobOffer, criteria: SearchCriteria) -> bool:
    return fits_language(offer, criteria) and fits_place(offer, criteria)


def fits_language(offer: JobOffer, criteria: SearchCriteria) -> bool:
    """An offer whose language is unknown is kept: better to show it than to miss it."""
    if not criteria.offer_languages or offer.language is None:
        return True
    return offer.language in criteria.offer_languages


def fits_place(offer: JobOffer, criteria: SearchCriteria) -> bool:
    work_mode = offer.work_mode or "onsite"
    if not criteria.accepts_work_mode(work_mode):
        return False
    if offer.country in criteria.countries:
        return True
    # Elsewhere, only remote jobs open to where the user lives
    return work_mode == "remote" and remote_region_accepts(
        offer.location, criteria.countries, criteria.open_to_remote_abroad
    )
