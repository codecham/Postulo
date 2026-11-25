from typing import Any

from fastapi.testclient import TestClient

from tests.conftest import LoginAs

SCHOOL_42 = {
    "school": "42 Paris",
    "degree": "RNCP level 7",
    "field_of_study": "Software engineering",
    "location": "Paris",
    "start_date": "2021-09-01",
    "end_date": "2024-06-01",
    "description": "Peer-to-peer learning, C and Python projects.",
}


def create(client: TestClient, headers: dict[str, str], **changes: Any) -> dict[str, Any]:
    """Create an education (SCHOOL_42, with optional changes) and return it."""
    response = client.post("/educations", json=SCHOOL_42 | changes, headers=headers)
    assert response.status_code == 201
    body: dict[str, Any] = response.json()
    return body


def test_create_returns_the_new_education(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")

    response = client.post("/educations", json=SCHOOL_42, headers=headers)

    assert response.status_code == 201
    assert response.json()["id"]
    assert response.json()["school"] == "42 Paris"


def test_list_shows_ongoing_studies_first_then_the_most_recent_and_undated_last(
    client: TestClient, login_as: LoginAs
) -> None:
    headers = login_as("alice@mail.com")
    create(client, headers, school="Undated", start_date=None, end_date=None)
    create(client, headers, school="Old", start_date="2010-09-01", end_date="2013-06-01")
    create(client, headers, school="Ongoing", start_date="2024-09-01", end_date=None)
    create(client, headers, school="Recent", start_date=None, end_date="2020-06-01")

    response = client.get("/educations", headers=headers)

    assert [item["school"] for item in response.json()] == ["Ongoing", "Recent", "Old", "Undated"]


def test_update_replaces_the_education(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")
    education = create(client, headers)

    response = client.put(
        f"/educations/{education['id']}", json={"school": "42 Lyon"}, headers=headers
    )

    assert response.status_code == 200
    assert response.json()["school"] == "42 Lyon"
    assert response.json()["degree"] is None


def test_delete_removes_the_education(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")
    education = create(client, headers)

    response = client.delete(f"/educations/{education['id']}", headers=headers)

    assert response.status_code == 204
    assert client.get("/educations", headers=headers).json() == []


def test_users_cannot_see_or_change_each_others_educations(
    client: TestClient, login_as: LoginAs
) -> None:
    alice = login_as("alice@mail.com")
    bob = login_as("bob@mail.com")
    alice_education_url = f"/educations/{create(client, alice)['id']}"

    bob_list = client.get("/educations", headers=bob)
    bob_update = client.put(alice_education_url, json=SCHOOL_42, headers=bob)
    bob_delete = client.delete(alice_education_url, headers=bob)

    assert bob_list.json() == []
    assert bob_update.status_code == 404
    assert bob_delete.status_code == 404


def test_educations_require_a_token(client: TestClient) -> None:
    assert client.get("/educations").status_code == 401
    assert client.post("/educations", json=SCHOOL_42).status_code == 401
