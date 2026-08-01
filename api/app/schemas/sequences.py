from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .common import Envelope


class SequenceRow(BaseModel):
    id: str | None = None
    name: str
    slug: str | None = None
    clips: int = 0
    target_duration: int | float | None = None
    health: str | None = None
    chain_qa_status: str | None = None
    raw: dict[str, Any] | None = None


class SequenceListOut(Envelope):
    sequences: list[SequenceRow]


class SequenceInitIn(BaseModel):
    name: str
    target_duration: int = Field(default=30, ge=1, le=600)


class SequenceInitOut(Envelope):
    sequence: SequenceRow
    message: str
