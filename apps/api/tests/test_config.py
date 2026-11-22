import pytest
from pydantic import ValidationError

from app.core.config import Settings


def make_settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("POSTGRES_USER", "alice")
    monkeypatch.setenv("POSTGRES_PASSWORD", "s3cret")
    monkeypatch.setenv("POSTGRES_DB", "postulo")
    monkeypatch.setenv("POSTGRES_HOST", "db")
    monkeypatch.setenv("POSTGRES_PORT", "6543")
    # _env_file=None: ignore the local .env so the test only sees the values above
    return Settings(_env_file=None)


def test_database_url_is_built_from_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = make_settings(monkeypatch)
    assert settings.database_url == "postgresql+psycopg://alice:s3cret@db:6543/postulo"


def test_port_is_converted_to_int(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = make_settings(monkeypatch)
    assert settings.postgres_port == 6543


def test_password_is_hidden_when_printed(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = make_settings(monkeypatch)
    assert "s3cret" not in str(settings)


def test_missing_required_variable_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
