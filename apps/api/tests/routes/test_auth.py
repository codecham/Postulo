import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.main import app
from app.models import User
from app.routes.auth import get_auth_throttle
from app.services.auth_throttle import AuthThrottle

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


def register_alice(client: TestClient) -> str:
    """Create Alice's account and return her user id."""
    response = client.post("/auth/register", json=VALID_USER)
    return str(response.json()["id"])


def test_login_returns_a_token_for_the_user(client: TestClient, db: Session) -> None:
    user_id = register_alice(client)

    response = client.post(
        "/auth/login", data={"username": "alice@mail.com", "password": "correct horse"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    settings = get_settings()
    payload = jwt.decode(
        body["access_token"],
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == user_id


def test_login_rejects_a_wrong_password(client: TestClient, db: Session) -> None:
    register_alice(client)

    response = client.post(
        "/auth/login", data={"username": "alice@mail.com", "password": "wrong password"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}


def test_login_rejects_an_unknown_email(client: TestClient, db: Session) -> None:
    response = client.post(
        "/auth/login", data={"username": "nobody@mail.com", "password": "correct horse"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}


def use_throttle(**limits: int) -> None:
    """Make the auth routes use small limits, so a test reaches them in a few calls."""
    settings = get_settings().model_copy(update=limits)
    throttle = AuthThrottle.from_settings(settings)
    app.dependency_overrides[get_auth_throttle] = lambda: throttle


def login_alice(client: TestClient, password: str = "correct horse") -> int:
    response = client.post("/auth/login", data={"username": "alice@mail.com", "password": password})
    return response.status_code


def test_login_is_refused_after_too_many_attempts_from_one_ip(
    client: TestClient, db: Session
) -> None:
    use_throttle(login_attempts_per_ip=2)
    register_alice(client)
    login_alice(client)
    login_alice(client)

    response = client.post(
        "/auth/login", data={"username": "alice@mail.com", "password": "correct horse"}
    )

    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0


def test_an_email_is_locked_after_too_many_failed_logins(client: TestClient, db: Session) -> None:
    use_throttle(failed_logins_per_email=2)
    register_alice(client)
    login_alice(client, "wrong password")
    login_alice(client, "wrong password")

    status_code = login_alice(client)  # even the right password must wait

    assert status_code == 429


def test_successful_logins_do_not_lock_the_email(client: TestClient, db: Session) -> None:
    use_throttle(failed_logins_per_email=2)
    register_alice(client)

    status_codes = [login_alice(client) for _ in range(3)]

    assert status_codes == [200, 200, 200]


def test_register_is_refused_after_too_many_accounts_from_one_ip(
    client: TestClient, db: Session
) -> None:
    use_throttle(registrations_per_ip=1)
    client.post("/auth/register", json=VALID_USER)

    response = client.post(
        "/auth/register", json={"email": "bob@mail.com", "password": "correct horse"}
    )

    assert response.status_code == 429


def test_register_is_refused_when_registration_is_closed(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "registration_open", False)

    response = client.post("/auth/register", json=VALID_USER)

    assert response.status_code == 403
    assert db.scalar(select(User)) is None


def test_login_rejects_a_password_longer_than_any_account_accepts(
    client: TestClient, db: Session
) -> None:
    register_alice(client)

    status_code = login_alice(client, "x" * 10_000)

    assert status_code == 401
