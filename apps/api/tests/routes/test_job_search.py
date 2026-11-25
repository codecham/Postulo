from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import LoginAs

SEARCHABLE_PROFILE = {"desired_titles": ["Python developer"], "skills": ["Python"]}


def login_with_profile(client: TestClient, login_as: LoginAs, email: str) -> dict[str, str]:
    headers = login_as(email)
    client.put("/profile/me", json=SEARCHABLE_PROFILE, headers=headers)
    return headers


def test_overview_without_any_search(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")

    response = client.get("/job-search", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["latest_run"] is None
    assert {source["name"] for source in body["sources"]} == {
        "remotive",
        "jobicy",
        "himalayas",
        "adzuna",
    }


def test_start_search_queues_a_run(client: TestClient, login_as: LoginAs) -> None:
    headers = login_with_profile(client, login_as, "alice@mail.com")

    response = client.post("/job-search/runs", headers=headers)

    assert response.status_code == 202
    assert response.json()["status"] == "pending"
    latest = client.get("/job-search", headers=headers).json()["latest_run"]
    assert latest["id"] == response.json()["id"]


def test_start_search_twice_is_a_conflict(client: TestClient, login_as: LoginAs) -> None:
    headers = login_with_profile(client, login_as, "alice@mail.com")
    client.post("/job-search/runs", headers=headers)

    response = client.post("/job-search/runs", headers=headers)

    assert response.status_code == 409


def test_start_search_needs_titles_or_skills(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")

    response = client.post("/job-search/runs", headers=headers)

    assert response.status_code == 422


def test_job_search_requires_a_login(client: TestClient, db: Session) -> None:
    assert client.get("/job-search").status_code == 401
    assert client.post("/job-search/runs").status_code == 401
