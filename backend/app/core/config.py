"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from environment and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Backend Server Settings
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000

    # PostgreSQL Database Settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = "documentai_thesis"
    TEST_DB_NAME: str = "documentai_thesis_test"

    # Local Document Storage Settings
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_DIR: str = "./storage/uploads"

    # Security
    SECRET_KEY: str = "development_secret_key_not_for_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_database_uri(self) -> str:
        """Construct the primary PostgreSQL connection URI using psycopg driver."""
        password_part = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return (
            f"postgresql+psycopg://{self.DB_USER}{password_part}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_test_database_uri(self) -> str:
        """Construct the test PostgreSQL connection URI for isolated integration tests."""
        password_part = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return (
            f"postgresql+psycopg://{self.DB_USER}{password_part}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.TEST_DB_NAME}"
        )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
