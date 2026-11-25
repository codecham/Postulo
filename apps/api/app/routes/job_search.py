"""Job search: see the last search, start one, read the matching offers.

The searches themselves run in the worker (app/worker.py), not in the API.
"""

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, status

from app.core.config import get_settings
from app.core.dependencies import CurrentUser, DbSession
from app.schemas.job_search import (
    JobMatchRead,
    JobSearchOverview,
    JobSearchRunRead,
    JobSourceRead,
)
from app.services.job_search import errors, matching, runs
from app.services.job_search.sources.registry import source_infos

router = APIRouter(prefix="/job-search", tags=["job search"])

HTTP_ERRORS: dict[type[errors.JobSearchError], tuple[int, str]] = {
    errors.ProfileIncompleteError: (
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "Add the job titles you are looking for (or skills) to your profile first",
    ),
    errors.SearchAlreadyActiveError: (status.HTTP_409_CONFLICT, "A search is already running"),
    errors.SearchRateLimitError: (
        status.HTTP_429_TOO_MANY_REQUESTS,
        "Too many searches today, the next daily search will run automatically",
    ),
}


def to_http_error(error: errors.JobSearchError) -> HTTPException:
    status_code, detail = HTTP_ERRORS[type(error)]
    return HTTPException(status_code=status_code, detail=detail)


def documented(*error_types: type[errors.JobSearchError]) -> dict[int | str, dict[str, Any]]:
    return {HTTP_ERRORS[error][0]: {"description": HTTP_ERRORS[error][1]} for error in error_types}


@router.get("")
def read_job_search(user: CurrentUser, db: DbSession) -> JobSearchOverview:
    """The user's last search and the job boards this server searches."""
    latest = runs.latest_run(db, user.id)
    return JobSearchOverview(
        latest_run=JobSearchRunRead.model_validate(latest) if latest else None,
        sources=[JobSourceRead.model_validate(info) for info in source_infos(get_settings())],
    )


@router.post(
    "/runs",
    status_code=status.HTTP_202_ACCEPTED,
    responses=documented(
        errors.ProfileIncompleteError,
        errors.SearchAlreadyActiveError,
        errors.SearchRateLimitError,
    ),
)
def start_search(user: CurrentUser, db: DbSession) -> JobSearchRunRead:
    """Ask the worker to search now, without waiting for the daily search."""
    per_day = get_settings().manual_job_searches_per_day
    try:
        run = runs.request_manual_run(db, user.id, per_day)
    except errors.JobSearchError as error:
        raise to_http_error(error) from None
    return JobSearchRunRead.model_validate(run)


@router.get("/matches")
def list_matches(
    user: CurrentUser, db: DbSession, limit: Annotated[int, Query(ge=1, le=100)] = 20
) -> list[JobMatchRead]:
    """The offers that fit the profile best."""
    return [JobMatchRead.model_validate(item) for item in matching.list_matches(db, user.id, limit)]
