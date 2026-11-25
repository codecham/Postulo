"""Why an offer matches: a few facts that the dashboard shows next to the score."""

from dataclasses import dataclass

from app.models import JobMatch, JobOffer
from app.schemas.job_match import MatchPlace
from app.services.job_search.criteria import SearchCriteria
from app.services.job_search.scoring import relevance


@dataclass(frozen=True)
class Explanation:
    relevance: int
    matched_skills: list[str]
    place: MatchPlace


def explain(match: JobMatch, criteria: SearchCriteria) -> Explanation:
    return Explanation(
        relevance=relevance(match.similarity),
        matched_skills=list(match.matched_skills),
        place=place_of(match.offer, criteria),
    )


def place_of(offer: JobOffer, criteria: SearchCriteria) -> MatchPlace:
    if offer.country is not None and offer.country in criteria.countries:
        return MatchPlace.YOUR_COUNTRY
    if offer.work_mode == "remote":
        return MatchPlace.REMOTE
    return MatchPlace.OTHER
