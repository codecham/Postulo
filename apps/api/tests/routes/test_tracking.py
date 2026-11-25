from datetime import date, timedelta
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import JobMatch, MatchStatus, User
from tests.conftest import LoginAs
from tests.services.job_search.helpers import add_match

TODAY = date.today()


def user_named(db: Session, email: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    assert user is not None
    return user


def setup_match(login_as: LoginAs, db: Session) -> tuple[dict[str, str], JobMatch]:
    headers = login_as("alice@mail.com")
    return headers, add_match(db, user_named(db, "alice@mail.com"), title="Python developer")


def url(match: JobMatch) -> str:
    return f"/job-search/matches/{match.id}/tracking"


def mark_as_sent(client: TestClient, headers: dict[str, str], match: JobMatch, **body: Any) -> Any:
    return client.post(url(match), json=body, headers=headers)


# --- Mark as sent ---


def test_mark_as_sent_starts_the_tracking_with_a_follow_up_in_a_week(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers, match = setup_match(login_as, db)

    response = mark_as_sent(client, headers, match)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "applied"
    assert body["applied_on"] == TODAY.isoformat()
    assert body["follow_up_on"] == (TODAY + timedelta(days=7)).isoformat()
    assert body["follow_up_due"] is False
    assert [event["status"] for event in body["events"]] == ["applied"]


def test_mark_as_sent_saves_a_new_match(client: TestClient, login_as: LoginAs, db: Session) -> None:
    headers, match = setup_match(login_as, db)

    mark_as_sent(client, headers, match)

    db.refresh(match)
    assert match.status == MatchStatus.SAVED


def test_mark_as_sent_twice_answers_409(client: TestClient, login_as: LoginAs, db: Session) -> None:
    headers, match = setup_match(login_as, db)
    mark_as_sent(client, headers, match)

    response = mark_as_sent(client, headers, match)

    assert response.status_code == 409


def test_mark_as_sent_rejects_a_follow_up_before_the_application(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers, match = setup_match(login_as, db)

    response = mark_as_sent(
        client, headers, match, applied_on="2026-11-20", follow_up_on="2026-11-10"
    )

    assert response.status_code == 422


def test_mark_as_sent_answers_404_for_someone_elses_match(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    _, match = setup_match(login_as, db)
    bob_headers = login_as("bob@mail.com")

    response = mark_as_sent(client, bob_headers, match)

    assert response.status_code == 404


# --- Update ---


def test_a_new_status_is_added_to_the_history(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers, match = setup_match(login_as, db)
    mark_as_sent(client, headers, match)

    response = client.patch(url(match), json={"status": "interview"}, headers=headers)

    body = response.json()
    assert body["status"] == "interview"
    assert [event["status"] for event in body["events"]] == ["applied", "interview"]


def test_update_only_changes_the_fields_sent(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers, match = setup_match(login_as, db)
    mark_as_sent(client, headers, match)

    body = client.patch(url(match), json={"notes": "Called HR"}, headers=headers).json()

    assert body["notes"] == "Called HR"
    assert body["status"] == "applied"
    assert body["follow_up_on"] is not None
    assert len(body["events"]) == 1


def test_update_can_remove_the_reminder_but_not_the_status(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers, match = setup_match(login_as, db)
    mark_as_sent(client, headers, match)

    removed = client.patch(url(match), json={"follow_up_on": None}, headers=headers)
    null_status = client.patch(url(match), json={"status": None}, headers=headers)

    assert removed.json()["follow_up_on"] is None
    assert null_status.status_code == 422


def test_a_past_follow_up_is_due_only_while_waiting(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers, match = setup_match(login_as, db)
    mark_as_sent(client, headers, match, applied_on="2026-01-01", follow_up_on="2026-01-08")

    waiting = client.get(url(match), headers=headers).json()
    rejected = client.patch(url(match), json={"status": "rejected"}, headers=headers).json()

    assert waiting["follow_up_due"] is True
    assert rejected["follow_up_due"] is False


def test_undo_removes_the_tracking(client: TestClient, login_as: LoginAs, db: Session) -> None:
    headers, match = setup_match(login_as, db)
    mark_as_sent(client, headers, match)

    response = client.delete(url(match), headers=headers)

    assert response.status_code == 204
    assert client.get(url(match), headers=headers).status_code == 404


# --- Board ---


def test_the_board_lists_the_sent_applications_with_their_offer_and_counts(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers, match = setup_match(login_as, db)
    other = add_match(db, user_named(db, "alice@mail.com"))
    mark_as_sent(client, headers, match)
    mark_as_sent(client, headers, other)
    client.patch(url(other), json={"status": "offer"}, headers=headers)

    body = client.get("/tracking", headers=headers).json()

    assert len(body["items"]) == 2
    assert body["items"][0]["offer"]["title"]
    assert body["counts"] == {
        "applied": 1,
        "interview": 0,
        "offer": 1,
        "rejected": 0,
        "withdrawn": 0,
    }


def test_the_board_only_shows_the_users_own_applications(
    client: TestClient, login_as: LoginAs, db: Session
) -> None:
    headers, match = setup_match(login_as, db)
    mark_as_sent(client, headers, match)
    bob_headers = login_as("bob@mail.com")

    body = client.get("/tracking", headers=bob_headers).json()

    assert body["items"] == []
