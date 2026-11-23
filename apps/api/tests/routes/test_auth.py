from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User

VALID_USER = {"email": "Alice@Mail.com", "password": "correct horse"}


def test_register_creates_user(client: TestClient, db: Session) -> None:
    response = client.post("/auth/register", json=VALID_USER)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@mail.com"
    assert body["is_active"] is True
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_stores_a_hashed_password(client: TestClient, db: Session) -> None:
    client.post("/auth/register", json=VALID_USER)

    user = db.scalar(select(User).where(User.email == "alice@mail.com"))

    assert user is not None
    assert user.hashed_password != VALID_USER["password"]
    assert user.hashed_password.startswith("$argon2")


def test_register_rejects_duplicate_email(client: TestClient, db: Session) -> None:
    client.post("/auth/register", json=VALID_USER)

    response = client.post(
        "/auth/register",
        json={"email": "ALICE@mail.com", "password": "another password"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}


def test_register_rejects_short_password(client: TestClient, db: Session) -> None:
    response = client.post("/auth/register", json={"email": "bob@mail.com", "password": "short"})

    assert response.status_code == 422


def test_register_rejects_invalid_email(client: TestClient, db: Session) -> None:
    response = client.post(
        "/auth/register", json={"email": "not-an-email", "password": "long enough"}
    )

    assert response.status_code == 422
