"""Shared CLI loaders and quota helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer

from aup_gate import AUPGateError
from character_dna import find_character_dna, load_character_dna
from models import normalize_chat_model
from project_state import load_project_state
from quota_optimizer import assess_budget_risk
from sequence_chain import find_sequence, get_clip, load_sequence

from cli.shared import console


def resolve_chat_model_cli(slug: str | None) -> str:
    """Resolve --chat-model for CLI; warn on unknown non-empty slugs.

    Default is grok-4.6 (cinematic). Use grok-4.3 / long-context only for 1M Bibles.
    """
    resolved, known = normalize_chat_model(slug)
    if slug and str(slug).strip() and not known:
        console.print(
            f"[yellow]Unknown chat model {slug!r}; using {resolved} "
            f"(cinematic default grok-4.6)[/yellow]"
        )
    return resolved


def require_character_dna_path(name: str) -> Path:
    path = find_character_dna(name)
    if not path:
        console.print(f"[red]No DNA profile found for:[/red] {name}")
        raise typer.Exit(1)
    return path


def require_character_dna(name: str) -> dict[str, Any]:
    try:
        return load_character_dna(require_character_dna_path(name))
    except AUPGateError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc


def require_sequence_bundle(name: str) -> tuple[dict[str, Any], Path]:
    path = find_sequence(name)
    if not path:
        console.print(f"[red]Sequence not found:[/red] {name}")
        raise typer.Exit(1)
    return load_sequence(path), path


def require_sequence(name: str) -> dict[str, Any]:
    seq, _ = require_sequence_bundle(name)
    return seq


def require_clip(seq: dict[str, Any], clip_id: str) -> dict[str, Any]:
    clip = get_clip(seq, clip_id)
    if not clip:
        console.print(f"[red]Clip not found:[/red] {clip_id}")
        raise typer.Exit(1)
    return clip


def assess_risk_from_state(estimate: dict[str, Any]) -> dict[str, Any]:
    state = load_project_state()
    quota = state.get("quota", {})
    return assess_budget_risk(
        estimate,
        tier=quota.get("tier", "supergrok_pro"),
        budget_remaining=quota.get("budget_remaining"),
    )