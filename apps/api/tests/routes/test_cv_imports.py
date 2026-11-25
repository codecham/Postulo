from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import get_settings
from app.main import app
from app.routes.cv_imports import get_cv_extractor
from tests.conftest import LoginAs
from tests.fakes import FakeCvExtractor, make_extraction, make_pdf


def upload(client: TestClient, headers: dict[str, str], content: bytes | None = None) -> Any:
    files = {"file": ("cv.pdf", make_pdf() if content is None else content, "application/pdf")}
    return client.post("/profile/imports", files=files, headers=headers)


def start(client: TestClient, headers: dict[str, str]) -> dict[str, Any]:
    """Upload a CV and return the created import."""
    response = upload(client, headers)
    assert response.status_code == 201
    body: dict[str, Any] = response.json()
    return body


def without_flag(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Draft items as the apply body expects them: without `already_exists`."""
    return [
        {key: value for key, value in item.items() if key != "already_exists"} for item in items
    ]


def apply(client: TestClient, headers: dict[str, str], cv_import: dict[str, Any]) -> Any:
    draft = cv_import["draft"]
    body = {
        "profile": draft["profile"],
        "experiences": without_flag(draft["experiences"]),
        "educations": without_flag(draft["educations"]),
    }
    return client.post(f"/profile/imports/{cv_import['id']}/apply", json=body, headers=headers)


# --- Upload ---


def test_upload_returns_a_draft_merged_with_the_current_profile(
    client: TestClient, login_as: LoginAs, fake_extractor: FakeCvExtractor
) -> None:
    headers = login_as("alice@mail.com")
    client.put("/profile/me", json={"skills": ["Docker"], "city": "Liège"}, headers=headers)

    body = start(client, headers)

    assert body["status"] == "pending_review"
    profile = body["draft"]["profile"]
    assert profile["full_name"] == "Alice Martin"
    assert profile["city"] == "Brussels"
    assert profile["skills"] == ["Docker", "Python", "PostgreSQL"]
    assert body["draft"]["experiences"][0]["already_exists"] is False
    assert body["draft"]["educations"][0]["school"] == "42 Paris"


def test_upload_does_not_change_the_profile(
    client: TestClient, login_as: LoginAs, fake_extractor: FakeCvExtractor
) -> None:
    headers = login_as("alice@mail.com")

    start(client, headers)

    assert client.get("/profile/me", headers=headers).json()["full_name"] is None
    assert client.get("/experiences", headers=headers).json() == []


def test_upload_requires_a_login(client: TestClient, fake_extractor: FakeCvExtractor) -> None:
    response = upload(client, headers={})

    assert response.status_code == 401


@pytest.mark.parametrize(
    ("content", "status_code"),
    [
        (b"not a pdf", 415),
        (b"%PDF-" + b"0" * (5 * 1024 * 1024), 413),
        (make_pdf(pages=11), 422),
    ],
)
def test_invalid_files_are_rejected_before_calling_the_ai(
    client: TestClient,
    login_as: LoginAs,
    fake_extractor: FakeCvExtractor,
    content: bytes,
    status_code: int,
) -> None:
    headers = login_as("alice@mail.com")

    response = upload(client, headers, content)

    assert response.status_code == status_code
    assert fake_extractor.calls == 0


def test_a_document_that_is_not_a_cv_is_rejected(
    client: TestClient, login_as: LoginAs, fake_extractor: FakeCvExtractor
) -> None:
    fake_extractor.extraction = make_extraction(is_cv=False)
    headers = login_as("alice@mail.com")

    response = upload(client, headers)

    assert response.status_code == 422


def test_an_ai_failure_answers_502(
    client: TestClient, login_as: LoginAs, fake_extractor: FakeCvExtractor
) -> None:
    fake_extractor.fail = True
    headers = login_as("alice@mail.com")

    response = upload(client, headers)

    assert response.status_code == 502


def test_imports_are_limited_per_hour_failures_included(
    client: TestClient, login_as: LoginAs, fake_extractor: FakeCvExtractor
) -> None:
    headers = login_as("alice@mail.com")
    fake_extractor.fail = True
    for _ in range(get_settings().cv_imports_per_hour):
        upload(client, headers)
    fake_extractor.fail = False

    response = upload(client, headers)

    assert response.status_code == 429
    assert fake_extractor.calls == get_settings().cv_imports_per_hour


def test_upload_answers_503_without_an_api_key(
    client: TestClient, login_as: LoginAs, monkeypatch: pytest.MonkeyPatch
) -> None:
    app.dependency_overrides.pop(get_cv_extractor, None)
    monkeypatch.setattr(get_settings(), "anthropic_api_key", None)
    headers = login_as("alice@mail.com")

    response = upload(client, headers)

    assert response.status_code == 503


# --- Read ---


def test_read_returns_the_import(
    client: TestClient, login_as: LoginAs, fake_extractor: FakeCvExtractor
) -> None:
    headers = login_as("alice@mail.com")
    cv_import = start(client, headers)

    response = client.get(f"/profile/imports/{cv_import['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json() == cv_import


def test_another_users_import_is_not_found(
    client: TestClient, login_as: LoginAs, fake_extractor: FakeCvExtractor
) -> None:
    cv_import = start(client, login_as("alice@mail.com"))
    bob = login_as("bob@mail.com")

    read = client.get(f"/profile/imports/{cv_import['id']}", headers=bob)
    applied = apply(client, bob, cv_import)

    assert read.status_code == 404
    assert applied.status_code == 404


# --- Apply and discard ---


def test_apply_saves_the_profile_and_the_experiences(
    client: TestClient, login_as: LoginAs, fake_extractor: FakeCvExtractor
) -> None:
    headers = login_as("alice@mail.com")
    cv_import = start(client, headers)

    response = apply(client, headers, cv_import)

    assert response.status_code == 200
    assert response.json()["status"] == "applied"
    assert response.json()["draft"] is None  # personal data is not kept twice
    assert client.get("/profile/me", headers=headers).json()["full_name"] == "Alice Martin"
    assert [item["company"] for item in client.get("/experiences", headers=headers).json()] == [
        "Acme"
    ]
    assert [item["school"] for item in client.get("/educations", headers=headers).json()] == [
        "42 Paris"
    ]


def test_an_import_cannot_be_applied_twice(
    client: TestClient, login_as: LoginAs, fake_extractor: FakeCvExtractor
) -> None:
    headers = login_as("alice@mail.com")
    cv_import = start(client, headers)
    apply(client, headers, cv_import)

    response = apply(client, headers, cv_import)

    assert response.status_code == 409
    assert len(client.get("/experiences", headers=headers).json()) == 1


def test_an_invalid_apply_saves_nothing(
    client: TestClient, login_as: LoginAs, fake_extractor: FakeCvExtractor
) -> None:
    headers = login_as("alice@mail.com")
    cv_import = start(client, headers)
    body = {"profile": {"countries": ["Belgium"]}, "experiences": []}

    url = f"/profile/imports/{cv_import['id']}"

    response = client.post(f"{url}/apply", json=body, headers=headers)

    assert response.status_code == 422
    assert client.get(url, headers=headers).json()["status"] == "pending_review"


def test_discard_closes_the_import_without_saving(
    client: TestClient, login_as: LoginAs, fake_extractor: FakeCvExtractor
) -> None:
    headers = login_as("alice@mail.com")
    cv_import = start(client, headers)

    response = client.post(f"/profile/imports/{cv_import['id']}/discard", headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == "discarded"
    assert client.get("/profile/me", headers=headers).json()["full_name"] is None


# --- From an extraction made in Claude Code ---


def test_an_extraction_from_claude_code_creates_a_draft_without_calling_the_ai(
    client: TestClient, login_as: LoginAs, fake_extractor: FakeCvExtractor
) -> None:
    headers = login_as("alice@mail.com")
    extraction = make_extraction().model_dump(mode="json")

    response = client.post("/profile/imports/from-extraction", json=extraction, headers=headers)

    assert response.status_code == 201
    assert response.json()["draft"]["profile"]["full_name"] == "Alice Martin"
    assert fake_extractor.calls == 0


def test_an_extraction_that_does_not_match_the_schema_is_rejected(
    client: TestClient, login_as: LoginAs
) -> None:
    headers = login_as("alice@mail.com")

    response = client.post(
        "/profile/imports/from-extraction", json={"full_name": "Alice"}, headers=headers
    )

    assert response.status_code == 422


def test_an_extraction_that_is_not_a_cv_is_rejected(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")
    extraction = make_extraction(is_cv=False).model_dump(mode="json")

    response = client.post("/profile/imports/from-extraction", json=extraction, headers=headers)

    assert response.status_code == 422
    assert response.json()["detail"] == "This document does not look like a CV or a profile"


# --- Options ---


@pytest.mark.parametrize(("api_key", "pdf_upload"), [(None, False), ("sk-test", True)])
def test_options_tell_whether_the_pdf_upload_works(
    client: TestClient,
    login_as: LoginAs,
    monkeypatch: pytest.MonkeyPatch,
    api_key: str | None,
    pdf_upload: bool,
) -> None:
    key = None if api_key is None else SecretStr(api_key)
    monkeypatch.setattr(get_settings(), "anthropic_api_key", key)
    headers = login_as("alice@mail.com")

    response = client.get("/profile/imports/options", headers=headers)

    assert response.json() == {"pdf_upload": pdf_upload}
