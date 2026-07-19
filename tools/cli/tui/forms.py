"""Cockpit form specs (compat re-exports from unified actions registry)."""

from __future__ import annotations

from cli.tui.actions import (  # noqa: F401
    COCKPIT_ORDER,
    COCKPIT_WORKFLOWS,
    FormField,
    VALID_QUOTA_TIERS,
    WorkflowSpec,
    answers_to_argv,
    default_answers,
    summarize_action,
    validate_answers,
)

__all__ = [
    "COCKPIT_ORDER",
    "COCKPIT_WORKFLOWS",
    "FormField",
    "VALID_QUOTA_TIERS",
    "WorkflowSpec",
    "answers_to_argv",
    "default_answers",
    "summarize_action",
    "validate_answers",
]
