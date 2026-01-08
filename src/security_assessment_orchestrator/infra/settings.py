from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    log_level: str = "INFO"

    auth_token: str = "change-me"
    allowed_targets: str = "localhost,127.0.0.1"

    database_url: str

    # Optional
    redis_url: str | None = None

        zap_base_url: str = 'http://zap:8090'

    def allowed_targets_list(self) -> list[str]:
        return [t.strip() for t in self.allowed_targets.split(",") if t.strip()]
