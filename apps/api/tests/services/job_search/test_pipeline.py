from sqlalchemy.orm import Session

from app.models import JobSearchRun, JobSearchRunStatus
from app.services.job_search import runs
from app.services.job_search.pipeline import SearchTools, execute_run
from tests.fakes import FakeEmbedder, FakeJobSource, make_collected_offer
from tests.services.job_search.helpers import create_user, matches_of

GOOD_OFFER = make_collected_offer(
    title="Python developer", description="Python FastAPI backend developer for our API."
)


def start_run(db: Session) -> JobSearchRun:
    user = create_user(db, headline="Python developer", summary="FastAPI backend API")
    runs.request_manual_run(db, user.id, per_day=5)
    run = runs.claim_next_run(db)
    assert run is not None
    return run


def tools(*sources: FakeJobSource) -> SearchTools:
    return SearchTools(sources=sources, embedder=FakeEmbedder(), min_score=30)


def test_a_search_collects_offers_and_saves_matches(db: Session) -> None:
    run = start_run(db)
    source = FakeJobSource(offers=[GOOD_OFFER])

    execute_run(db, run, tools(source))

    assert run.status == JobSearchRunStatus.SUCCEEDED
    assert (run.offers_found, run.offers_new, run.matches_found) == (1, 1, 1)
    assert source.criteria[0].keywords == ("Python developer",)
    assert [match.offer.title for match in matches_of(db, run.user_id)] == ["Python developer"]


def test_a_failing_job_board_does_not_stop_the_others(db: Session) -> None:
    run = start_run(db)
    broken = FakeJobSource(name="broken")
    broken.fail = True

    execute_run(db, run, tools(broken, FakeJobSource(offers=[GOOD_OFFER])))

    assert run.status == JobSearchRunStatus.SUCCEEDED
    assert run.failed_sources == ["broken"]
    assert run.matches_found == 1


def test_the_search_fails_when_no_job_board_answers(db: Session) -> None:
    run = start_run(db)
    broken = FakeJobSource(name="broken")
    broken.fail = True

    execute_run(db, run, tools(broken))

    assert run.status == JobSearchRunStatus.FAILED
    assert run.error == "No job board could be reached"
    assert run.finished_at is not None
