from fastapi.testclient import TestClient

from tests.conftest import LoginAs

FULL_PROFILE = {
    "full_name": "Alice Martin",
    "headline": "Backend developer",
    "summary": "Five years of Python.",
    "city": "Brussels",
    "skills": ["Python", "FastAPI"],
    "languages": ["fr", "en"],
    "desired_titles": ["Backend developer"],
    "work_modes": ["remote", "hybrid"],
    "countries": ["BE"],
    "open_to_remote_abroad": True,
    "offer_languages": ["fr", "en", "nl"],
}


def test_a_new_user_gets_an_empty_profile(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")

    response = client.get("/profile/me", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] is None
    assert body["skills"] == []


def test_a_new_profile_searches_belgium_and_remote_jobs_in_french_or_english(
    client: TestClient, login_as: LoginAs
) -> None:
    headers = login_as("alice@mail.com")

    body = client.get("/profile/me", headers=headers).json()

    assert body["countries"] == ["BE"]
    assert body["open_to_remote_abroad"] is True
    assert body["offer_languages"] == ["fr", "en"]


def test_update_saves_the_whole_profile(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")

    client.put("/profile/me", json=FULL_PROFILE, headers=headers)
    response = client.get("/profile/me", headers=headers)

    assert response.status_code == 200
    body = response.json()
    for field, value in FULL_PROFILE.items():
        assert body[field] == value


def test_update_replaces_the_previous_values(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")
    client.put("/profile/me", json=FULL_PROFILE, headers=headers)

    response = client.put("/profile/me", json={"skills": ["Go"]}, headers=headers)

    body = response.json()
    assert body["skills"] == ["Go"]
    assert body["full_name"] is None  # a missing field is reset: PUT replaces everything


def test_update_rejects_an_invalid_work_mode(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")

    response = client.put("/profile/me", json={"work_modes": ["sometimes"]}, headers=headers)

    assert response.status_code == 422


def test_each_user_has_their_own_profile(client: TestClient, login_as: LoginAs) -> None:
    alice = login_as("alice@mail.com")
    bob = login_as("bob@mail.com")
    client.put("/profile/me", json=FULL_PROFILE, headers=alice)

    response = client.get("/profile/me", headers=bob)

    assert response.json()["full_name"] is None


def test_profile_requires_a_token(client: TestClient) -> None:
    assert client.get("/profile/me").status_code == 401
    assert client.put("/profile/me", json={}).status_code == 401
