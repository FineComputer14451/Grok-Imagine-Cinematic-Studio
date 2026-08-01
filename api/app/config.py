from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "GICS Snapshot API"
    studio_version: str = "3.8.9"
    api_prefix: str = "/api/v1"
    # When set, require matching X-API-Key header
    studio_api_key: str | None = None
    # Repo root (parent of tools/). Empty → auto-detect or mock mode.
    studio_root: str | None = None
    cors_origins: str = "http://127.0.0.1:8080,http://localhost:8080,http://127.0.0.1:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def resolve_studio_root() -> Path | None:
    settings = get_settings()
    if settings.studio_root:
        root = Path(settings.studio_root).expanduser().resolve()
        return root if root.is_dir() else None

    # api/ is at <repo>/api → parent is monorepo root when checked in
    here = Path(__file__).resolve()
    candidates = [
        here.parents[2],  # <repo>/api/app/config.py → <repo>
        Path.cwd(),
        Path.cwd().parent,
    ]
    for root in candidates:
        if (root / "tools" / "cinematic_studio_cli.py").is_file():
            return root
    return None
