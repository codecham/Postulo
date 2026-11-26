from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models import JobSearchRun, JobSearchRunStatus, JobSearchTrigger
from app.services.job_search import runs
from app.services.job_search.errors import (
    ProfileIncompleteError,
    SearchAlreadyActiveError,
    SearchRateLimitError,
)
from tests.services.job_search.helpers import create_user

DAY = timedelta(days=1)


def finish(db: Session, run: JobSearchRun) -> None:
    runs.finish_run(run, JobSearchRunStatus.SUCCEEDED)
    db.commit()


def test_request_manual_run_queues_a_pending_run(db: Session) -> None:
    user = create_user(db)

    run = runs.request_manual_run(db, user.id, per_day=5)

    assert run.status == JobSearchRunStatus.PENDING
    assert run.trigger == JobSearchTrigger.MANUAL
    assert runs.latest_run(db, user.id) == run


def test_a_profile_without_titles_or_skills_cannot_search(db: Session) -> None:
    user = create_user(db, desired_titles=[], skills=[], headline=None)

    with pytest.raises(ProfileIncompleteError):
        runs.request_manual_run(db, user.id, per_day=5)


def test_only_one_search_at_a_time(db: Session) -> None:
    user = create_user(db)
    runs.request_manual_run(db, user.id, per_day=5)

    with pytest.raises(SearchAlreadyActiveError):
        runs.request_manual_run(db, user.id, per_day=5)


def test_manual_searches_are_limited_per_day(db: Session) -> None:
    user = create_user(db)
    finish(db, runs.request_manual_run(db, user.id, per_day=2))
    finish(db, runs.request_manual_run(db, user.id, per_day=2))

    with pytest.raises(SearchRateLimitError):
        runs.request_manual_run(db, user.id, per_day=2)


def test_schedule_due_runs_queues_users_without_a_recent_search(db: Session) -> None:
    due = create_user(db, "due@mail.com")
    recent = create_user(db, "recent@mail.com")
    create_user(db, "empty@mail.com", desired_titles=[], skills=[])
    finish(db, runs.request_manual_run(db, recent.id, per_day=5))

    scheduled = runs.schedule_due_runs(db, interval=DAY)

    assert [run.user_id for run in scheduled] == [due.id]
    assert scheduled[0].trigger == JobSearchTrigger.SCHEDULED


def test_schedule_due_runs_queues_again_after_the_interval(db: Session) -> None:
    user = create_user(db)
    run = runs.request_manual_run(db, user.id, per_day=5)
    finish(db, run)
    run.created_at = datetime.now(UTC) - 2 * DAY
    db.commit()

    assert [run.user_id for run in runs.schedule_due_runs(db, interval=DAY)] == [user.id]


def test_claim_next_run_takes_the_oldest_pending_run(db: Session) -> None:
    alice = create_user(db, "alice@mail.com")
    bob = create_user(db, "bob@mail.com")
    first = runs.request_manual_run(db, alice.id, per_day=5)
    runs.request_manual_run(db, bob.id, per_day=5)

    claimed = runs.claim_next_run(db)

    assert claimed == first
    assert claimed.status == JobSearchRunStatus.RUNNING
    assert claimed.started_at is not None


def test_claim_next_run_returns_none_when_the_queue_is_empty(db: Session) -> None:
    assert runs.claim_next_run(db) is None


def test_fail_stale_runs_closes_runs_left_running(db: Session) -> None:
    user = create_user(db)
    runs.request_manual_run(db, user.id, per_day=5)
    run = runs.claim_next_run(db)
    assert run is not None
    run.started_at = datetime.now(UTC) - timedelta(hours=2)
    db.commit()

    closed = runs.fail_stale_runs(db)

    assert closed == 1
    assert run.status == JobSearchRunStatus.FAILED


def test_request_hunt_run_queues_a_scheduled_run_without_rate_limit(db: Session) -> None:
    user = create_user(db)
    for _ in range(3):
        finish(db, runs.request_manual_run(db, user.id, per_day=3))

    run = runs.request_hunt_run(db, user.id)

    assert run.status == JobSearchRunStatus.PENDING
    assert run.trigger == JobSearchTrigger.SCHEDULED


def test_request_hunt_run_gives_the_active_run(db: Session) -> None:
    user = create_user(db)
    active = runs.request_manual_run(db, user.id, per_day=5)

    assert runs.request_hunt_run(db, user.id) == active


def test_request_hunt_run_needs_a_searchable_profile(db: Session) -> None:
    user = create_user(db, desired_titles=[], skills=[])

    with pytest.raises(ProfileIncompleteError):
        runs.request_hunt_run(db, user.id)
