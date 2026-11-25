"""The matches dashboard: list, filter and count a user's matches, and triage them."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import ColumnElement, Select, UnaryExpression, func, select
from sqlalchemy.orm import InstrumentedAttribute, Session, contains_eager

from app.models import JobMatch, JobOffer, MatchStatus
from app.schemas.job_match import MatchFacets, MatchQuery, MatchSort
from app.services.job_search.errors import MatchNotFoundError

# The date of an offer: when the job board published it, or when we found it
OFFER_DATE = func.coalesce(JobOffer.published_at, JobOffer.created_at)
# An offer that does not say how it works is on site (as for the search criteria)
OFFER_WORK_MODE = func.coalesce(JobOffer.work_mode, "onsite")


def list_matches(
    db: Session, user_id: uuid.UUID, query: MatchQuery
) -> tuple[Sequence[JobMatch], int]:
    """One page of the user's matches with the query's status and filters, and their total."""
    conditions = [*filter_conditions(user_id, query), JobMatch.status == query.status]
    page = (
        _with_offer(select(JobMatch))
        .options(contains_eager(JobMatch.offer))
        .where(*conditions)
        .order_by(*_ordering(query.sort))
        .limit(query.limit)
        .offset(query.offset)
    )
    total = db.scalar(_with_offer(select(func.count(JobMatch.id))).where(*conditions))
    return db.scalars(page).all(), total or 0


def count_by_status(db: Session, user_id: uuid.UUID, query: MatchQuery) -> dict[MatchStatus, int]:
    """How many matches of each status pass the query's filters."""
    rows = db.execute(
        _with_offer(select(JobMatch.status, func.count(JobMatch.id)))
        .where(*filter_conditions(user_id, query))
        .group_by(JobMatch.status)
    ).all()
    counts = {MatchStatus(status): count for status, count in rows}
    return {status: counts.get(status, 0) for status in MatchStatus}


def match_facets(db: Session, user_id: uuid.UUID) -> MatchFacets:
    """The sources, countries and languages found in the user's matches."""
    return MatchFacets(
        sources=_distinct_offer_values(db, user_id, JobOffer.source),
        countries=_distinct_offer_values(db, user_id, JobOffer.country),
        languages=_distinct_offer_values(db, user_id, JobOffer.language),
    )


def get_match(db: Session, user_id: uuid.UUID, match_id: uuid.UUID) -> JobMatch:
    match = db.scalar(select(JobMatch).where(JobMatch.id == match_id, JobMatch.user_id == user_id))
    if match is None:
        raise MatchNotFoundError
    return match


def set_status(
    db: Session, user_id: uuid.UUID, match_id: uuid.UUID, status: MatchStatus
) -> JobMatch:
    """Save, dismiss or restore a match."""
    match = get_match(db, user_id, match_id)
    match.status = status
    db.commit()
    db.refresh(match)
    return match


def shortlist(db: Session, user_id: uuid.UUID, match_id: uuid.UUID) -> None:
    """Save a match the user acts on (writes or sends an application), if it is new.

    Not committed: the caller commits it with its own changes.
    """
    match = get_match(db, user_id, match_id)
    if match.status == MatchStatus.NEW:
        match.status = MatchStatus.SAVED


def filter_conditions(user_id: uuid.UUID, query: MatchQuery) -> list[ColumnElement[bool]]:
    """The query's filters, all but the status (the tabs count every status)."""
    conditions = [JobMatch.user_id == user_id, JobMatch.score >= query.min_score]
    if query.work_mode:
        conditions.append(OFFER_WORK_MODE.in_(query.work_mode))
    if query.country:
        conditions.append(JobOffer.country.in_(query.country))
    if query.language:
        conditions.append(JobOffer.language.in_(query.language))
    if query.source:
        conditions.append(JobOffer.source.in_(query.source))
    if query.max_age_days is not None:
        since = datetime.now(UTC) - timedelta(days=query.max_age_days)
        conditions.append(since <= OFFER_DATE)
    return conditions


def _with_offer[*Ts](statement: Select[*Ts]) -> Select[*Ts]:
    return statement.select_from(JobMatch).join(JobOffer, JobOffer.id == JobMatch.offer_id)


def _ordering(sort: MatchSort) -> tuple[UnaryExpression[Any] | InstrumentedAttribute[Any], ...]:
    # The id last: a stable order, so no match shows on two pages
    if sort == MatchSort.DATE:
        return (OFFER_DATE.desc(), JobMatch.score.desc(), JobMatch.id)
    return (JobMatch.score.desc(), OFFER_DATE.desc(), JobMatch.id)


def _distinct_offer_values(
    db: Session, user_id: uuid.UUID, column: InstrumentedAttribute[Any]
) -> list[str]:
    values = db.scalars(
        _with_offer(select(column).distinct())
        .where(JobMatch.user_id == user_id, column.is_not(None))
        .order_by(column)
    ).all()
    return [str(value) for value in values]
