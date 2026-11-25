from typing import Any

from fastapi.testclient import TestClient

from tests.conftest import LoginAs

DEVELOPER = {
    "title": "Developer",
    "company": "Acme",
    "location": "Brussels",
    "start_date": "2022-01-01",
    "end_date": "2024-06-01",
    "description": "Built the billing API.",
}


def create(client: TestClient, headers: dict[str, str], **changes: Any) -> dict[str, Any]:
    """Create an experience (DEVELOPER, with optional changes) and return it."""
    response = client.post("/experiences", json=DEVELOPER | changes, headers=headers)
    assert response.status_code == 201
    body: dict[str, Any] = response.json()
    return body


def test_create_returns_the_new_experience(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")

    response = client.post("/experiences", json=DEVELOPER, headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["title"] == "Developer"
    assert body["end_date"] == "2024-06-01"


def test_list_shows_current_jobs_first_then_the_most_recent(
    client: TestClient, login_as: LoginAs
) -> None:
    headers = login_as("alice@mail.com")
    create(client, headers, title="Old", start_date="2015-01-01", end_date="2016-01-01")
    create(client, headers, title="Current", start_date="2023-01-01", end_date=None)
    create(client, headers, title="Recent", start_date="2020-01-01", end_date="2022-12-01")

    response = client.get("/experiences", headers=headers)

    assert [item["title"] for item in response.json()] == ["Current", "Recent", "Old"]


def test_update_replaces_the_experience(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")
    experience = create(client, headers)

    response = client.put(
        f"/experiences/{experience['id']}",
        json=DEVELOPER | {"title": "Lead developer", "end_date": None},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Lead developer"
    assert response.json()["end_date"] is None


def test_delete_removes_the_experience(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")
    experience = create(client, headers)

    response = client.delete(f"/experiences/{experience['id']}", headers=headers)

    assert response.status_code == 204
    assert client.get("/experiences", headers=headers).json() == []


def test_end_date_before_start_date_is_rejected(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")

    response = client.post(
        "/experiences",
        json=DEVELOPER | {"start_date": "2024-01-01", "end_date": "2023-01-01"},
        headers=headers,
    )

    assert response.status_code == 422


def test_users_cannot_see_or_change_each_others_experiences(
    client: TestClient, login_as: LoginAs
) -> None:
    alice = login_as("alice@mail.com")
    bob = login_as("bob@mail.com")
    alice_experience_url = f"/experiences/{create(client, alice)['id']}"

    bob_list = client.get("/experiences", headers=bob)
    bob_update = client.put(alice_experience_url, json=DEVELOPER, headers=bob)
    bob_delete = client.delete(alice_experience_url, headers=bob)

    assert bob_list.json() == []
    # 404, not 403: Bob must not even learn that this experience exists
    assert bob_update.status_code == 404
    assert bob_delete.status_code == 404


def test_unknown_experience_returns_404(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")

    response = client.delete("/experiences/00000000-0000-0000-0000-000000000000", headers=headers)

    assert response.status_code == 404


def test_experiences_require_a_token(client: TestClient) -> None:
    assert client.get("/experiences").status_code == 401
    assert client.post("/experiences", json=DEVELOPER).status_code == 401
