from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from tests.conftest import LoginAs


def test_me_returns_the_logged_in_user(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")

    response = client.get("/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "alice@mail.com"


def test_me_requires_a_token(client: TestClient, db: Session) -> None:
    response = client.get("/users/me")

    assert response.status_code == 401


def test_me_rejects_a_forged_token(client: TestClient, login_as: LoginAs) -> None:
    headers = login_as("alice@mail.com")
    forged = headers["Authorization"][:-4] + "abcd"  # change the end of the signature

    response = client.get("/users/me", headers={"Authorization": forged})

    assert response.status_code == 401


def test_me_rejects_an_expired_token(client: TestClient, db: Session) -> None:
    settings = get_settings()
    expired = jwt.encode(
        {"sub": "any-id", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    response = client.get("/users/me", headers={"Authorization": f"Bearer {expired}"})

    assert response.status_code == 401
