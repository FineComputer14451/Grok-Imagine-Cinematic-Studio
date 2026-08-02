"""Unified TUI action registry — re-exports from studio_core (PR2).

Implementation lives in ``studio_core.services.actions`` so Web/API shells can
share the same ActionSpec catalog without importing Textual. This module keeps
the historical import path ``cli.tui.actions`` stable for TUI screens and tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from studio_core.services.actions import *  # noqa: E402,F403
from studio_core.services.actions import (  # noqa: E402,F401
    ACTIONS,
    COCKPIT_GROUP_LABELS,
    COCKPIT_ORDER,
    COCKPIT_WORKFLOWS,
    FORBIDDEN_ARGV_TOKENS,
    FormField,
    LAUNCHER_CATALOG,
    LAUNCHER_ORDER,
    ActionSpec,
    LauncherEntry,
    Surface,
    VALID_ASPECTS,
    VALID_QUOTA_TIERS,
    WorkflowSpec,
    actions_for,
    answers_to_argv,
    default_answers,
    filter_palette_actions,
    get_action,
    menu_rows,
    palette_actions,
    reject_forbidden_argv,
    static_allowed_argvs,
    summarize_action,
    validate_answers,
)

__all__ = [
    "ACTIONS",
    "COCKPIT_GROUP_LABELS",
    "COCKPIT_ORDER",
    "COCKPIT_WORKFLOWS",
    "FORBIDDEN_ARGV_TOKENS",
    "FormField",
    "LAUNCHER_CATALOG",
    "LAUNCHER_ORDER",
    "ActionSpec",
    "LauncherEntry",
    "Surface",
    "VALID_ASPECTS",
    "VALID_QUOTA_TIERS",
    "WorkflowSpec",
    "actions_for",
    "answers_to_argv",
    "default_answers",
    "filter_palette_actions",
    "get_action",
    "menu_rows",
    "palette_actions",
    "reject_forbidden_argv",
    "static_allowed_argvs",
    "summarize_action",
    "validate_answers",
]
