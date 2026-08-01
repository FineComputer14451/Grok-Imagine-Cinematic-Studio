from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Envelope(BaseModel):
    """Wraps payloads with source metadata."""

    source: Literal["live", "mock"] = "mock"
    studio_version: str = "3.8.9"


class ErrorBody(BaseModel):
    detail: str
    code: str | None = None


class HealthOut(BaseModel):
    status: Literal["ok", "degraded"]
    studio_version: str
    tools_available: bool
    studio_root: str | None = None


class CliActionIn(BaseModel):
    timeout_sec: int = Field(default=120, ge=5, le=600)
    args: list[str] = Field(default_factory=list)


class CliActionOut(Envelope):
    action: str
    exit_code: int
    output: str
    ok: bool


class SeverityOut(BaseModel):
    severity: Literal["ok", "warn", "critical"]
    label: str
    attention: list[str] = Field(default_factory=list)


class SnapshotOut(Envelope):
    severity: Literal["ok", "warn", "critical"] = "ok"
    attention: list[str] = Field(default_factory=list)
    snapshot: dict[str, Any]
