from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.main import app
from app.models import JobMatch, MatchStatus, User
from app.routes.applications import get_application_writer
from tests.conftest import LoginAs
from tests.fakes import FakeApplicationWriter, make_generated_application
from tests.services.job_search.helpers import add_match

PROFILE = {"full_name": "Alice Martin", "city": "Brussels", "skills": ["Python"]}


def user_named(db: Session, email: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    assert user is not None
    return user


def setup_match(
    client: TestClient, login_as: LoginAs, db: Session, **offer_changes: Any
) -> tuple[dict[str, str], JobMatch]:
    """Alice, with a filled profile and one match."""
    headers = login_as("alice@mail.com")
    client.put("/profile/me", json=PROFILE, headers=headers)
    match = add_match(db, user_named(db, "alice@mail.com"), **offer_changes)
    return headers, match


def url(match: JobMatch, path: str = "") -> str:
    return f"/job-search/matches/{match.id}/application{path}"


def generate(client: TestClient, headers: dict[str, str], match: JobMatch) -> Any:
    return client.post(url(match, "/generate"), headers=headers)


# --- Generation ---


def test_generate_writes_the_application_in_the_offer_language(
    client: TestClient, login_as: LoginAs, db: Session, fake_writer: FakeApplicationWriter
) -> None:
    headers, match = setup_match(client, login_as, db, language="fr")

    response = generate(client, headers, match)

    assert response.status_code == 201
    body = response.json()
    assert body["model"] == "fake-model"
    assert body["content"]["language"] == "fr"
    assert body["content"]["cv"]["headline"] == "Python backend developer"
    assert fake_writer.contexts[0].offer["title"] == "Python developer"


def test_generate_saves_a_new_match_so_the_next_search_keeps_it(
    client: TestClient, login_as: LoginAs, db: Session, fake_writer: FakeApplicationWriter
) -> None:
    headers, match = setup_match(client, login_as, db)

    generate(client, headers, match)

    db.refresh(match)
    assert match.status == MatchStatus.SAVED


def test_generate_fills_the_contact_from_the_account_and_the_profile(
    client: TestClient, login_as: LoginAs, db: Session, fake_writer: FakeApplicationWriter
) -> None:
    headers, match = setup_match(client, login_as, db)

    contact = generate(client, headers, match).json()["content"]["contact"]

    assert contact == {
        "full_name": "Alice Martin",
        "email": "alice@mail.com",
        "phone": None,
        "city": "Brussels",
        "links": [],
    }


def test_generate_refuses_an_empty_profile(
    client: TestClient, login_as: LoginAs, db: Session, fake_writer: FakeApplicationWriter
) -> None:
    headers = login_as("alice@mail.com")
    match = add_match(db, user_named(db, "alice@mail.com"))

    response = generate(client, headers, match)

    assert response.status_code == 422
    assert fake_writer.contexts == []


def test_generate_answers_404_for_someone_elses_match(
    client: TestClient, login_as: LoginAs, db: Session, fake_writer: FakeApplicationWriter
) -> None:
    _, match = setup_match(client, login_as, db)
    bob_headers = login_as("bob@mail.com")

    response = generate(client, bob_headers, match)

    assert response.status_code == 404


def test_generate_answers_502_when_the_ai_fails(
    client: TestClient, login_as: LoginAs, db: Session, fake_writer: FakeApplicationWriter
) -> None:
    headers, match = setup_match(client, login_as, db)
    fake_writer.fail = True

    response = generate(client, headers, match)

    assert response.status_code == 502
    assert client.get(url(match), headers=headers).status_code == 404


def test_generate_is_rate_limited(
    client: TestClient,
    login_as: LoginAs,
    db: Session,
    fake_writer: FakeApplicationWriter,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(get_settings(), "applications_per_hour", 1)
    headers, match = setup_match(client, login_as, db)
    generate(client, headers, match)

    response = generate(client, headers, match)

    assert response.status_code == 429


def test_generate_answers_503_without_an_api_key(
    client: TestClient, login_as: LoginAs, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "anthropic_api_key", None)
    app.dependency_overrides.pop(get_application_writer, None)
    headers, match = setup_match(client, login_as, db)

    response = generate(client, headers, match)

    assert response.status_code == 503


# --- Claude Code (free path) ---


def test_from_claude_code_saves_the_pasted_application(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers, match = setup_match(client, login_as, db, language="en")
    pasted = make_generated_application().model_dump(mode="json")

    response = client.post(url(match, "/from-claude-code"), json=pasted, headers=headers)

    assert response.status_code == 201
    assert response.json()["model"] == "claude-code"
    assert response.json()["content"]["language"] == "en"


def test_from_claude_code_rejects_json_that_breaks_the_schema(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers, match = setup_match(client, login_as, db)
    pasted = make_generated_application().model_dump(mode="json")
    pasted["cv"]["experiences"][0]["start_month"] = "January 2022"

    response = client.post(url(match, "/from-claude-code"), json=pasted, headers=headers)

    assert response.status_code == 422


def test_claude_code_applications_are_not_rate_limited(
    client: TestClient, login_as: LoginAs, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "applications_per_hour", 1)
    headers, match = setup_match(client, login_as, db)
    pasted = make_generated_application().model_dump(mode="json")
    client.post(url(match, "/from-claude-code"), json=pasted, headers=headers)

    response = client.post(url(match, "/from-claude-code"), json=pasted, headers=headers)

    assert response.status_code == 201


# --- Read, edit, download ---


def test_read_gives_the_latest_application(
    client: TestClient, login_as: LoginAs, db: Session, fake_writer: FakeApplicationWriter
) -> None:
    headers, match = setup_match(client, login_as, db)
    generate(client, headers, match)
    fake_writer.application = make_generated_application(
        cv=make_generated_application().cv.model_copy(update={"headline": "Second version"})
    )
    generate(client, headers, match)

    response = client.get(url(match), headers=headers)

    assert response.json()["content"]["cv"]["headline"] == "Second version"


def test_read_answers_404_before_any_generation(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers, match = setup_match(client, login_as, db)

    response = client.get(url(match), headers=headers)

    assert response.status_code == 404


def test_update_saves_the_reviewed_content(
    client: TestClient, login_as: LoginAs, db: Session, fake_writer: FakeApplicationWriter
) -> None:
    headers, match = setup_match(client, login_as, db)
    content = generate(client, headers, match).json()["content"]
    content["contact"]["phone"] = "+32 470 00 00 00"
    content["cover_letter"]["paragraphs"] = ["A shorter letter."]

    response = client.put(url(match), json=content, headers=headers)

    assert response.status_code == 200
    saved = client.get(url(match), headers=headers).json()["content"]
    assert saved["contact"]["phone"] == "+32 470 00 00 00"
    assert saved["cover_letter"]["paragraphs"] == ["A shorter letter."]


def test_update_rejects_a_letter_without_paragraphs(
    client: TestClient, login_as: LoginAs, db: Session, fake_writer: FakeApplicationWriter
) -> None:
    headers, match = setup_match(client, login_as, db)
    content = generate(client, headers, match).json()["content"]
    content["cover_letter"]["paragraphs"] = []

    response = client.put(url(match), json=content, headers=headers)

    assert response.status_code == 422


@pytest.mark.parametrize("document", ["/cv.pdf", "/cover-letter.pdf"])
def test_download_gives_a_pdf_file(
    client: TestClient,
    login_as: LoginAs,
    db: Session,
    fake_writer: FakeApplicationWriter,
    document: str,
) -> None:
    headers, match = setup_match(client, login_as, db)
    generate(client, headers, match)

    response = client.get(url(match, document), headers=headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")


def test_download_answers_404_for_someone_else(
    client: TestClient, login_as: LoginAs, db: Session, fake_writer: FakeApplicationWriter
) -> None:
    headers, match = setup_match(client, login_as, db)
    generate(client, headers, match)
    bob_headers = login_as("bob@mail.com")

    response = client.get(url(match, "/cv.pdf"), headers=bob_headers)

    assert response.status_code == 404


# --- Options ---


@pytest.mark.parametrize(("api_key", "expected"), [(None, False), (SecretStr("key"), True)])
def test_options_tell_whether_ai_generation_works(
    client: TestClient,
    login_as: LoginAs,
    monkeypatch: pytest.MonkeyPatch,
    api_key: SecretStr | None,
    expected: bool,
) -> None:
    monkeypatch.setattr(get_settings(), "anthropic_api_key", api_key)
    headers = login_as("alice@mail.com")

    response = client.get("/applications/options", headers=headers)

    assert response.json() == {"ai_generation": expected}
