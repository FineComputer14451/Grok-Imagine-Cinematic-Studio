from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .common import Envelope


class QuotaEstimateIn(BaseModel):
    duration_sec: int = Field(default=60, ge=1, le=3600)
    complexity: str = "medium"
    fast_mode: bool = False
    video_model: str | None = None
    tier: str = "supergrok_pro"


class QuotaOut(Envelope):
    dashboard: dict[str, Any] = Field(default_factory=dict)
    estimate: dict[str, Any] | None = None
    risk: dict[str, Any] | None = None
    alignment: dict[str, Any] | None = None
