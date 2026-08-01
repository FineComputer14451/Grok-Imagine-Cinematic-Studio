from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .common import Envelope


class DnaProfile(BaseModel):
    id: str | None = None
    name: str
    slug: str | None = None
    status: str = "pending"
    locked: bool = False
    drift_score: float | None = None
    traits: list[str] = Field(default_factory=list)
    looks: str | None = None
    project: str | None = None
    raw: dict[str, Any] | None = None


class DnaListOut(Envelope):
    characters: list[DnaProfile]


class DnaLockIn(BaseModel):
    name: str | None = None
    slug: str | None = None


class DnaLockOut(Envelope):
    character: DnaProfile
    message: str
