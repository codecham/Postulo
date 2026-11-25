import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MatchStatus, User
from tests.conftest import LoginAs
from tests.services.job_search.helpers import add_match


def user_named(db: Session, email: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    assert user is not None
    return user


def test_list_matches_gives_a_page_with_explanations(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers = login_as("alice@mail.com")
    alice = user_named(db, "alice@mail.com")
    add_match(db, alice, score=80, title="Python developer")
    add_match(db, alice, score=60, status=MatchStatus.SAVED)

    response = client.get("/job-search/matches", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["counts"] == {"new": 1, "saved": 1, "dismissed": 0}
    [match] = body["items"]
    assert match["offer"]["title"] == "Python developer"
    assert match["explanation"]["matched_skills"] == ["Python"]
    assert match["explanation"]["place"] in {"your_country", "remote", "other"}


def test_list_matches_reads_list_filters_from_the_query(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers = login_as("alice@mail.com")
    alice = user_named(db, "alice@mail.com")
    add_match(db, alice, source="remotive")
    add_match(db, alice, source="jobicy")
    add_match(db, alice, source="adzuna")

    response = client.get(
        "/job-search/matches?source=remotive&source=jobicy&sort=date", headers=headers
    )

    assert response.json()["total"] == 2


def test_list_matches_rejects_an_unknown_filter_value(
    client: TestClient, login_as: LoginAs
) -> None:
    headers = login_as("alice@mail.com")

    response = client.get("/job-search/matches?work_mode=moon", headers=headers)

    assert response.status_code == 422


def test_update_match_changes_its_status(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers = login_as("alice@mail.com")
    match = add_match(db, user_named(db, "alice@mail.com"))

    response = client.patch(
        f"/job-search/matches/{match.id}", json={"status": "saved"}, headers=headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "saved"
    saved = client.get("/job-search/matches?status=saved", headers=headers).json()
    assert [item["id"] for item in saved["items"]] == [str(match.id)]


def test_read_match_gives_one_match(client: TestClient, login_as: LoginAs, db: Session) -> None:
    headers = login_as("alice@mail.com")
    match = add_match(db, user_named(db, "alice@mail.com"))

    response = client.get(f"/job-search/matches/{match.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["offer"]["description"] == "Build our API."


def test_the_matches_of_others_are_not_found(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    login_as("alice@mail.com")
    match = add_match(db, user_named(db, "alice@mail.com"))
    bob = login_as("bob@mail.com")

    read = client.get(f"/job-search/matches/{match.id}", headers=bob)
    update = client.patch(
        f"/job-search/matches/{match.id}", json={"status": "dismissed"}, headers=bob
    )

    assert (read.status_code, update.status_code) == (404, 404)


def test_facets_list_the_sources_of_the_matches(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers = login_as("alice@mail.com")
    add_match(db, user_named(db, "alice@mail.com"), source="remotive")

    response = client.get("/job-search/matches/facets", headers=headers)

    assert response.json()["sources"] == ["remotive"]


def test_matches_require_a_login(client: TestClient, db: Session) -> None:
    assert client.get("/job-search/matches").status_code == 401
    assert client.get(f"/job-search/matches/{uuid.uuid4()}").status_code == 401
