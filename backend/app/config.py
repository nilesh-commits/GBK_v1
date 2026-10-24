"""Application configuration (pydantic-settings).

All values are overridable via environment variables (or a local .env). The
purchasing cutoff default is a *provisional assumption* (12:00 Europe/London on
the decision day), not an official market deadline — see docs/04-methodology.md.
"""
from __future__ import annotations

from datetime import date
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    # Elexon BMRS API (no key required).
    elexon_base_url: str = "https://data.elexon.co.uk/bmrs/api/v1"

    # Purchasing cutoff — resolved as <cutoff_local_time> in <cutoff_timezone>
    # on the DECISION day. Provisional; configurable; never silently midnight.
    cutoff_local_time: str = "12:00"
    cutoff_timezone: str = "Europe/London"

    # In-scope decision dates (decision-anchored). Delivery day = decision + 1.
    decision_date_min: date = date(2026, 1, 1)
    decision_date_max: date = date(2026, 1, 31)

    # CORS: origins allowed to call the API (the frontend).
    cors_allowed_origins: list[str] = ["http://localhost:5173"]

    # Where the parquet cache lives (relative to the backend working dir).
    data_dir: str = "data"

    # Outbound HTTP (ingestion only).
    http_timeout_seconds: float = 30.0
    http_max_retries: int = 3


@lru_cache
def get_settings() -> Settings:
    return Settings()
