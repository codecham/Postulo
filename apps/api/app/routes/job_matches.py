"""The matches dashboard: the offers that fit the user, filtered, ranked and triaged."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser, DbSession
from app.models import JobMatch, MatchStatus
from app.schemas.job_match import (
    JobMatchPage,
    JobMatchRead,
    JobMatchUpdate,
    MatchExplanation,
    MatchFacets,
    MatchQuery,
    MatchStatusCounts,
)
from app.schemas.job_search import JobOfferRead
from app.services import profiles
from app.services.job_search import dashboard
from app.services.job_search.criteria import SearchCriteria
from app.services.job_search.errors import MatchNotFoundError
from app.services.job_search.explanation import explain

router = APIRouter(prefix="/job-search/matches", tags=["job matches"])

NOT_FOUND: dict[int | str, dict[str, Any]] = {
    status.HTTP_404_NOT_FOUND: {"description": "No such match"}
}


@router.get("")
def list_matches(
    user: CurrentUser, db: DbSession, query: Annotated[MatchQuery, Query()]
) -> JobMatchPage:
    """The user's matches with one status, filtered and ranked, plus the count of each tab."""
    matches, total = dashboard.list_matches(db, user.id, query)
    counts = dashboard.count_by_status(db, user.id, query)
    criteria = _criteria(db, user.id)
    return JobMatchPage(
        items=[to_match_read(match, criteria) for match in matches],
        total=total,
        counts=MatchStatusCounts(**counts),
    )


@router.get("/facets")
def read_facets(user: CurrentUser, db: DbSession) -> MatchFacets:
    """The values to offer in the filters: only those found in the user's matches."""
    return dashboard.match_facets(db, user.id)


@router.get("/{match_id}", responses=NOT_FOUND)
def read_match(match_id: uuid.UUID, user: CurrentUser, db: DbSession) -> JobMatchRead:
    try:
        match = dashboard.get_match(db, user.id, match_id)
    except MatchNotFoundError:
        raise _not_found() from None
    return to_match_read(match, _criteria(db, user.id))


@router.patch("/{match_id}", responses=NOT_FOUND)
def update_match(
    match_id: uuid.UUID, data: JobMatchUpdate, user: CurrentUser, db: DbSession
) -> JobMatchRead:
    """Save the offer to the shortlist, dismiss it, or put it back to review."""
    try:
        match = dashboard.set_status(db, user.id, match_id, data.status)
    except MatchNotFoundError:
        raise _not_found() from None
    return to_match_read(match, _criteria(db, user.id))


def to_match_read(match: JobMatch, criteria: SearchCriteria) -> JobMatchRead:
    return JobMatchRead(
        id=match.id,
        score=match.score,
        status=MatchStatus(match.status),
        created_at=match.created_at,
        offer=JobOfferRead.model_validate(match.offer),
        explanation=MatchExplanation.model_validate(explain(match, criteria)),
    )


def _criteria(db: Session, user_id: uuid.UUID) -> SearchCriteria:
    return SearchCriteria.from_profile(profiles.get_or_create_profile(db, user_id))


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
