from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

# The .env file at the repository root, two levels above apps/api.
# Inside Docker this file does not exist: Compose passes real environment variables.
API_DIR = Path(__file__).resolve().parents[2]
ROOT_ENV_FILE = API_DIR.parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings, read from environment variables.

    Real environment variables take precedence over the values in the .env file.
    A missing or invalid value stops the app at startup with a clear error.
    """

    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        # The shared .env also holds variables for other services (e.g. WEB_PORT)
        extra="ignore",
    )

    app_name: str = "API"

    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # At least 32 characters: shorter HMAC keys can be brute-forced
    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Browser origins allowed to call the API directly.
    # In .env, write it as JSON: CORS_ORIGINS=["http://localhost:3000"]
    cors_origins: list[str] = ["http://localhost:3000"]

    # CV import with Claude. Without a key the app still starts: the import answers 503.
    anthropic_api_key: SecretStr | None = None
    # Haiku: about 0.1 cent per CV, accurate enough for this extraction
    cv_import_model: str = "claude-haiku-5-5"
    cv_import_max_bytes: int = Field(default=5 * 1024 * 1024, gt=0)
    cv_import_max_pages: int = Field(default=10, gt=0)
    # Each import costs money: limit how many a user can start per hour
    cv_imports_per_hour: int = Field(default=5, gt=0)

    # Tailored CV and cover letter, written by Claude (same API key as the CV import)
    application_model: str = "claude-haiku-5-5"
    # Each AI generation costs money: limit how many a user can start per hour
    applications_per_hour: int = Field(default=10, gt=0)

    # Job search worker
    # Free key from https://developer.adzuna.com: adds Belgian (and other) on-site offers.
    # Without it, the search only uses the job boards that need no key (remote jobs).
    adzuna_app_id: str | None = None
    adzuna_app_key: SecretStr | None = None
    # Local, free embedding model (https://huggingface.co/minishlab), downloaded once
    embedding_model: str = "minishlab/potion-multilingual-128M"
    # Hours between two automatic searches for the same user
    job_search_interval_hours: int = Field(default=24, gt=0)
    # Searches a user can start by hand per day: public job boards ask for few calls
    manual_job_searches_per_day: int = Field(default=5, gt=0)
    # How often the worker looks for searches to run
    worker_poll_seconds: float = Field(default=10, gt=0)
    # Below this score (0-100), an offer is not saved as a match
    job_match_min_score: int = Field(default=50, ge=0, le=100)

    @field_validator("adzuna_app_id", "adzuna_app_key", mode="before")
    @classmethod
    def empty_adzuna_means_none(cls, value: object) -> object:
        return None if value == "" else value

    @field_validator("anthropic_api_key", mode="before")
    @classmethod
    def empty_key_means_no_key(cls, value: object) -> object:
        # Compose passes ANTHROPIC_API_KEY="" when .env leaves it empty
        return None if value == "" else value

    @property
    def database_url(self) -> str:
        # URL.create escapes special characters in the password
        url = URL.create(
            "postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )
        return url.render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    """Return the settings, read from the environment only once."""
    return Settings()
