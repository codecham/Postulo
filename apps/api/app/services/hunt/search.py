"""Run the hunt's search: save the browser findings, then let the worker score them.

The worker embeds every offer that has no embedding yet and scores all recent offers,
so the offers found in the browser are matched exactly like the job boards' ones.
"""

import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models import JobSearchRun, JobSearchRunStatus
from app.schemas.hunt import BrowserFindings
from app.services.hunt.findings import to_collected_offers
from app.services.job_search import runs
from app.services.job_search.offers import SavedOffers, save_offers


class HuntSearchTimeoutError(Exception):
    """The worker did not finish the search in time (is it running?)."""


def save_findings(db: Session, findings: BrowserFindings) -> SavedOffers:
    return save_offers(db, to_collected_offers(findings))


def wait_for_run(
    db: Session,
    run: JobSearchRun,
    timeout: timedelta,
    sleep: Callable[[float], None],
    poll_seconds: float = 3,
) -> JobSearchRun:
    """Wait until the worker finished the run, and return it as it ended."""
    deadline = datetime.now(UTC) + timeout
    while True:
        db.refresh(run)
        if run.status not in runs.ACTIVE_STATUSES:
            return run
        if datetime.now(UTC) >= deadline:
            raise HuntSearchTimeoutError(run.id)
        db.commit()  # end the read transaction, so the next refresh sees the worker's work
        sleep(poll_seconds)


def run_search(
    db: Session,
    user_id: uuid.UUID,
    findings: BrowserFindings,
    timeout: timedelta,
    sleep: Callable[[float], None],
) -> tuple[SavedOffers, JobSearchRun]:
    """Save the findings, queue a search, and wait for the worker to finish it."""
    saved = save_findings(db, findings)
    run = runs.request_hunt_run(db, user_id)
    if run.status == JobSearchRunStatus.RUNNING:
        # It started before the findings were saved and may miss them: run another one
        wait_for_run(db, run, timeout, sleep)
        run = runs.request_hunt_run(db, user_id)
    return saved, wait_for_run(db, run, timeout, sleep)
