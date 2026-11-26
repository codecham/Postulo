"""Job search runs: the queue between the API (which asks) and the worker (which runs).

A run goes pending -> running -> succeeded or failed. The API inserts manual runs; the
worker inserts the daily ones, then claims pending runs one at a time.
"""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import JobSearchRun, JobSearchRunStatus, JobSearchTrigger, Profile, User
from app.services import profiles
from app.services.job_search.criteria import SearchCriteria
from app.services.job_search.errors import (
    ProfileIncompleteError,
    SearchAlreadyActiveError,
    SearchRateLimitError,
)

ACTIVE_STATUSES = (JobSearchRunStatus.PENDING, JobSearchRunStatus.RUNNING)
RATE_LIMIT_WINDOW = timedelta(days=1)
# A run still "running" after this long was cut short (worker restarted or crashed)
STALE_AFTER = timedelta(hours=1)


def latest_run(db: Session, user_id: uuid.UUID) -> JobSearchRun | None:
    return db.scalar(
        select(JobSearchRun)
        .where(JobSearchRun.user_id == user_id)
        .order_by(JobSearchRun.created_at.desc())
        .limit(1)
    )


def request_manual_run(db: Session, user_id: uuid.UUID, per_day: int) -> JobSearchRun:
    """Queue a search the user asked for. The worker picks it up within seconds."""
    profile = profiles.get_or_create_profile(db, user_id)
    if not SearchCriteria.from_profile(profile).is_searchable:
        raise ProfileIncompleteError
    if _has_active_run(db, user_id):
        raise SearchAlreadyActiveError
    if _manual_runs_since(db, user_id, datetime.now(UTC) - RATE_LIMIT_WINDOW) >= per_day:
        raise SearchRateLimitError
    return _queue(db, user_id, JobSearchTrigger.MANUAL)


def request_hunt_run(db: Session, user_id: uuid.UUID) -> JobSearchRun:
    """Queue a search for the daily hunt, or give the one already waiting or running.

    Not rate limited: the hunt runs once a day, on the user's own machine.
    """
    profile = profiles.get_or_create_profile(db, user_id)
    if not SearchCriteria.from_profile(profile).is_searchable:
        raise ProfileIncompleteError
    active = _active_run(db, user_id)
    return active or _queue(db, user_id, JobSearchTrigger.SCHEDULED)


def schedule_due_runs(db: Session, interval: timedelta) -> list[JobSearchRun]:
    """Queue the daily search of every user whose last search is older than `interval`."""
    due_before = datetime.now(UTC) - interval
    return [
        _queue(db, profile.user_id, JobSearchTrigger.SCHEDULED)
        for profile in _active_profiles(db)
        if SearchCriteria.from_profile(profile).is_searchable
        and _last_run_created_at(db, profile.user_id, default=due_before) <= due_before
        and not _has_active_run(db, profile.user_id)
    ]


def claim_next_run(db: Session) -> JobSearchRun | None:
    """Take the oldest pending run and mark it running.

    SKIP LOCKED lets several workers share the queue without taking the same run.
    """
    run = db.scalar(
        select(JobSearchRun)
        .where(JobSearchRun.status == JobSearchRunStatus.PENDING)
        .order_by(JobSearchRun.created_at)
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    if run is None:
        return None
    run.status = JobSearchRunStatus.RUNNING
    run.started_at = datetime.now(UTC)
    db.commit()
    return run


def fail_stale_runs(db: Session) -> int:
    """Close the runs a stopped worker left running, so the user can search again."""
    stale = db.scalars(
        select(JobSearchRun).where(
            JobSearchRun.status == JobSearchRunStatus.RUNNING,
            JobSearchRun.started_at < datetime.now(UTC) - STALE_AFTER,
        )
    ).all()
    for run in stale:
        finish_run(run, JobSearchRunStatus.FAILED, error="The search was interrupted")
    db.commit()
    return len(stale)


def finish_run(run: JobSearchRun, status: JobSearchRunStatus, error: str | None = None) -> None:
    """Close a run without committing (the caller commits)."""
    run.status = status
    run.error = error
    run.finished_at = datetime.now(UTC)


def _queue(db: Session, user_id: uuid.UUID, trigger: JobSearchTrigger) -> JobSearchRun:
    run = JobSearchRun(user_id=user_id, trigger=trigger, status=JobSearchRunStatus.PENDING)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def _active_profiles(db: Session) -> Sequence[Profile]:
    return db.scalars(
        select(Profile).join(User, User.id == Profile.user_id).where(User.is_active)
    ).all()


def _has_active_run(db: Session, user_id: uuid.UUID) -> bool:
    return _active_run(db, user_id) is not None


def _active_run(db: Session, user_id: uuid.UUID) -> JobSearchRun | None:
    return db.scalar(
        select(JobSearchRun)
        .where(JobSearchRun.user_id == user_id, JobSearchRun.status.in_(ACTIVE_STATUSES))
        .order_by(JobSearchRun.created_at)
        .limit(1)
    )


def _manual_runs_since(db: Session, user_id: uuid.UUID, since: datetime) -> int:
    count = db.scalar(
        select(func.count())
        .select_from(JobSearchRun)
        .where(
            JobSearchRun.user_id == user_id,
            JobSearchRun.trigger == JobSearchTrigger.MANUAL,
            JobSearchRun.created_at >= since,
        )
    )
    return count or 0


def _last_run_created_at(db: Session, user_id: uuid.UUID, default: datetime) -> datetime:
    run = latest_run(db, user_id)
    return run.created_at if run is not None else default
