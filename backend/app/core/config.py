"""Application settings, loaded from environment variables (or a .env file)."""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET = "dev-only-secret-change-me-dev-only-secret"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["dev", "prod"] = "dev"
    database_url: str = "sqlite:///./dev.db"
    secret_key: str = DEFAULT_SECRET
    access_token_expire_minutes: int = 30

    # Uploads
    upload_dir: Path = Path("./uploads")
    max_upload_bytes: int = 5 * 1024 * 1024
    max_pdf_pages: int = 15
    max_text_chars: int = 200_000
    max_docx_uncompressed_bytes: int = 30 * 1024 * 1024
    max_documents_per_user: int = 50

    # Retention: uploaded files and their analyses are deleted after this many days
    retention_days: int = 30
    retention_sweep_interval_seconds: int = 3600
    retention_sweep_enabled: bool = True

    # Rate limiting (in-memory, per process)
    rate_limit_enabled: bool = True

    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @model_validator(mode="after")
    def _check_production_secret(self) -> "Settings":
        if self.environment == "prod" and (
            self.secret_key == DEFAULT_SECRET or len(self.secret_key) < 32
        ):
            raise ValueError("SECRET_KEY must be set to a random value of 32+ characters in prod")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
