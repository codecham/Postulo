"""Run one job search: collect offers, embed them, score them against the profile."""

import logging
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import JobSearchRun, JobSearchRunStatus
from app.services import experiences, profiles
from app.services.job_search.criteria import SearchCriteria
from app.services.job_search.embeddings import Embedder, profile_text
from app.services.job_search.errors import SourceError
from app.services.job_search.matching import match_offers
from app.services.job_search.offer import CollectedOffer
from app.services.job_search.offers import embed_pending_offers, save_offers
from app.services.job_search.runs import finish_run
from app.services.job_search.sources.base import JobSource

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SearchTools:
    """What a search needs from the outside world: real in the worker, fakes in tests."""

    sources: Sequence[JobSource]
    embedder: Embedder
    min_score: int


@dataclass(frozen=True)
class Collected:
    offers: list[CollectedOffer]
    failed_sources: list[str]


def execute_run(db: Session, run: JobSearchRun, tools: SearchTools) -> None:
    """Do the search of a running run and record its outcome. Never raises SourceError."""
    criteria = SearchCriteria.from_profile(profiles.get_or_create_profile(db, run.user_id))
    collected = collect_offers(tools.sources, criteria)
    saved = save_offers(db, collected.offers)
    run.offers_found, run.offers_new = saved.found, saved.new
    run.failed_sources = collected.failed_sources

    if tools.sources and len(collected.failed_sources) == len(tools.sources):
        finish_run(run, JobSearchRunStatus.FAILED, error="No job board could be reached")
        db.commit()
        return

    embed_pending_offers(db, tools.embedder)
    vector = tools.embedder.embed([build_profile_text(db, run)])[0]
    run.matches_found = match_offers(db, run.user_id, criteria, vector, tools.min_score)
    finish_run(run, JobSearchRunStatus.SUCCEEDED)
    db.commit()


def collect_offers(sources: Sequence[JobSource], criteria: SearchCriteria) -> Collected:
    """Ask every job board. One board failing does not stop the others."""
    offers: list[CollectedOffer] = []
    failed: list[str] = []
    for source in sources:
        try:
            offers.extend(source.fetch(criteria))
        except SourceError as error:
            logger.warning("Job board %s failed: %s", source.name, error)
            failed.append(source.name)
    return Collected(offers, failed)


def build_profile_text(db: Session, run: JobSearchRun) -> str:
    profile = profiles.get_or_create_profile(db, run.user_id)
    return profile_text(profile, experiences.list_experiences(db, run.user_id))
