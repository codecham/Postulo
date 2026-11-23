from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables.

    Real environment variables (e.g. set by Docker Compose) take precedence
    over the values in the .env file.
    """

    model_config = SettingsConfigDict(
        # Path relative to apps/api, where the API is run locally.
        # Ignored when the file does not exist (e.g. inside Docker).
        env_file="../../.env",
        # The shared .env also holds variables for other services (e.g. API_PORT)
        extra="ignore",
    )

    app_name: str = "Postulo API"

    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # At least 32 characters: shorter HMAC keys can be brute-forced
    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @property
    def database_url(self) -> str:
        password = self.postgres_password.get_secret_value()
        return (
            f"postgresql+psycopg://{self.postgres_user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Return the settings, read from the environment only once."""
    return Settings()
