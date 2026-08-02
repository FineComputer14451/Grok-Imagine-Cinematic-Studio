"""Service-layer facades over domain tools (no UI framework imports)."""

from __future__ import annotations

from studio_core.services.actions import (
    ACTIONS,
    ActionSpec,
    answers_to_argv,
    validate_answers,
)
from studio_core.services.dashboard import build_studio_dashboard

__all__ = [
    "ACTIONS",
    "ActionSpec",
    "answers_to_argv",
    "build_studio_dashboard",
    "validate_answers",
]
