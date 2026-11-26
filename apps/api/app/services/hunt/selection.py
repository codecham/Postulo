"""Which matches the hunt works on: the ones to write for, and the ones ready to send."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Application, JobMatch, JobOffer, MatchStatus, TrackedApplication
from app.services.job_search.dashboard import OFFER_DATE

# Older offers are often filled already: the hunt only writes for fresh ones
CANDIDATE_MAX_AGE = timedelta(days=21)


def list_candidates(db: Session, user_id: uuid.UUID, limit: int) -> Sequence[JobMatch]:
    """The best new matches without an application: the ones to write for today."""
    since = datetime.now(UTC) - CANDIDATE_MAX_AGE
    return db.scalars(
        select(JobMatch)
        .join(JobOffer, JobOffer.id == JobMatch.offer_id)
        .where(
            JobMatch.user_id == user_id,
            JobMatch.status == MatchStatus.NEW,
            JobMatch.id.not_in(select(Application.match_id)),
            JobMatch.id.not_in(select(TrackedApplication.match_id)),
            since <= OFFER_DATE,
        )
        .order_by(JobMatch.score.desc(), OFFER_DATE.desc())
        .limit(limit)
    ).all()


def list_ready(db: Session, user_id: uuid.UUID) -> Sequence[JobMatch]:
    """The shortlisted matches with an application that was not sent yet, oldest first."""
    written_at = (
        select(Application.match_id, func.max(Application.created_at).label("written_at"))
        .where(Application.user_id == user_id)
        .group_by(Application.match_id)
        .subquery()
    )
    return db.scalars(
        select(JobMatch)
        .join(written_at, written_at.c.match_id == JobMatch.id)
        .where(
            JobMatch.user_id == user_id,
            JobMatch.status == MatchStatus.SAVED,
            JobMatch.id.not_in(select(TrackedApplication.match_id)),
        )
        .order_by(written_at.c.written_at)
    ).all()
