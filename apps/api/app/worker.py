"""Background worker: runs the job searches. Start it with `python -m app.worker`.

Every few seconds it queues the daily search of each user who is due, then runs the
pending searches one by one (daily ones and those users asked for in the app).
"""

import logging
import signal
import threading
from datetime import timedelta
from pathlib import Path
from types import FrameType

import httpx

from app.core.config import Settings, get_settings
from app.core.database import SessionLocal
from app.core.logging import configure_logging
from app.models import JobSearchRunStatus
from app.services.job_search import runs
from app.services.job_search.embeddings import Model2VecEmbedder
from app.services.job_search.pipeline import SearchTools, execute_run
from app.services.job_search.sources.registry import build_sources

logger = logging.getLogger("app.worker")

HTTP_TIMEOUT_SECONDS = 20
# Identifies the worker to the job boards without revealing anything about its users
USER_AGENT = "job-search-worker/1.0"
# Touched on every loop: the container health check fails when it gets too old
HEARTBEAT_FILE = Path("/tmp/worker-heartbeat")


def main() -> None:
    settings = get_settings()
    configure_logging(settings)
    beat()
    stop = _stop_on_signals()
    with httpx.Client(timeout=HTTP_TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT}) as client:
        tools = SearchTools(
            sources=build_sources(settings, client),
            embedder=Model2VecEmbedder(settings.embedding_model),
            min_score=settings.job_match_min_score,
        )
        logger.info("Worker started with job boards: %s", [s.name for s in tools.sources])
        _close_stale_runs()
        while not stop.is_set():
            beat()
            run_pending_work(settings, tools)
            stop.wait(settings.worker_poll_seconds)
    logger.info("Worker stopped")


def run_pending_work(settings: Settings, tools: SearchTools) -> None:
    """Queue the searches that are due, then run every pending one."""
    with SessionLocal() as db:
        interval = timedelta(hours=settings.job_search_interval_hours)
        for run in runs.schedule_due_runs(db, interval):
            logger.info("Scheduled the daily search %s", run.id)
    while process_next_run(tools):
        beat()


def process_next_run(tools: SearchTools) -> bool:
    """Run the oldest pending search. False when there was none."""
    with SessionLocal() as db:
        run = runs.claim_next_run(db)
        if run is None:
            return False
        logger.info("Search %s started", run.id)
        try:
            execute_run(db, run, tools)
        except Exception:
            # Unexpected bug: record it on the run and keep the worker alive for the others
            logger.exception("Search %s crashed", run.id)
            db.rollback()
            runs.finish_run(run, JobSearchRunStatus.FAILED, error="Unexpected error")
            db.commit()
        logger.info(
            "Search %s %s: %s offers (%s new), %s matches",
            run.id,
            run.status,
            run.offers_found,
            run.offers_new,
            run.matches_found,
        )
        return True


def beat() -> None:
    """Record that the worker is alive and its loop is turning."""
    HEARTBEAT_FILE.touch()


def _close_stale_runs() -> None:
    with SessionLocal() as db:
        if count := runs.fail_stale_runs(db):
            logger.warning("Closed %s searches left running by a previous worker", count)


def _stop_on_signals() -> threading.Event:
    """An event set by Ctrl+C or `docker compose stop`: the current search ends first."""
    stop = threading.Event()

    def request_stop(signum: int, frame: FrameType | None) -> None:
        logger.info("Stopping after the current search…")
        stop.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    return stop


if __name__ == "__main__":
    main()
