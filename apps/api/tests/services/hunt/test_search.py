from datetime import timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import JobOffer, JobSearchRunStatus
from app.schemas.hunt import BrowserFindings
from app.services.hunt import search
from app.services.job_search import runs
from app.services.job_search.pipeline import SearchTools, execute_run
from tests.fakes import FakeEmbedder, FakeJobSource
from tests.services.hunt.helpers import make_browser_offer
from tests.services.job_search.helpers import create_user, matches_of

TIMEOUT = timedelta(minutes=1)


class FakeWorker:
    """A sleep that runs the pending search, as the real worker would meanwhile."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.sleeps = 0

    def __call__(self, seconds: float) -> None:
        self.sleeps += 1
        run = runs.claim_next_run(self.db)
        if run is not None:
            tools = SearchTools(sources=[FakeJobSource()], embedder=FakeEmbedder(), min_score=30)
            execute_run(self.db, run, tools)


def test_the_browser_offers_are_saved_and_matched(db: Session) -> None:
    user = create_user(db, headline="Python developer", summary="FastAPI backend API")
    findings = BrowserFindings(offers=[make_browser_offer()])

    saved, run = search.run_search(db, user.id, findings, TIMEOUT, FakeWorker(db))

    assert (saved.found, saved.new) == (1, 1)
    assert run.status == JobSearchRunStatus.SUCCEEDED
    assert [match.offer.source for match in matches_of(db, user.id)] == ["linkedin"]


def test_known_browser_offers_are_not_saved_twice(db: Session) -> None:
    findings = BrowserFindings(offers=[make_browser_offer()])
    search.save_findings(db, findings)

    saved = search.save_findings(db, findings)

    assert (saved.found, saved.new) == (1, 0)
    assert len(db.scalars(select(JobOffer)).all()) == 1


def test_a_search_already_running_is_followed_by_a_new_one(db: Session) -> None:
    user = create_user(db, headline="Python developer", summary="FastAPI backend API")
    runs.request_manual_run(db, user.id, per_day=5)
    started = runs.claim_next_run(db)
    assert started is not None
    worker = FakeWorker(db)
    findings = BrowserFindings(offers=[make_browser_offer()])

    def finish_started_then_work(seconds: float) -> None:
        if started.status == JobSearchRunStatus.RUNNING:
            runs.finish_run(started, JobSearchRunStatus.SUCCEEDED)
            db.commit()
        else:
            worker(seconds)

    _, run = search.run_search(db, user.id, findings, TIMEOUT, finish_started_then_work)

    assert run.id != started.id
    assert run.status == JobSearchRunStatus.SUCCEEDED
    assert worker.sleeps == 1


def test_waiting_stops_at_the_timeout(db: Session) -> None:
    user = create_user(db)
    run = runs.request_hunt_run(db, user.id)

    with pytest.raises(search.HuntSearchTimeoutError):
        search.wait_for_run(db, run, timedelta(0), sleep=lambda seconds: None)
