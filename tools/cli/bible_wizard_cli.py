"""Interactive Production Bible wizard (CLI I/O only).

Uses pure stage data from ``bible_stages``; assembly via ``build_production_bible``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import typer
from rich.panel import Panel

from cli.bible_stages import (
    STAGES,
    answers_to_kwargs,
    build_notes,
    validate_answers,
)
from cli.production import build_production_bible
from cli.shared import console


def _prompt_line(label: str) -> str:
    try:
        return input(label)
    except EOFError as exc:
        raise typer.Exit(1) from exc
    except KeyboardInterrupt as exc:
        console.print("\n[yellow]Wizard cancelled[/yellow]")
        raise typer.Exit(1) from exc


def _apply_field_value(field: dict[str, Any], raw: str, answers: dict[str, Any]) -> None:
    key = field["key"]
    text = raw.strip()
    if not text:
        # Empty enter: keep existing seed/answer, else field default, else clear
        existing = answers.get(key)
        if existing is not None and not (isinstance(existing, str) and not str(existing).strip()):
            return
        if field["default"] is not None:
            answers[key] = field["default"]
        else:
            answers[key] = None
        return
    if key == "target_duration_seconds":
        answers[key] = text  # answers_to_kwargs int()s
        return
    answers[key] = text


def run_bible_wizard(
    *,
    seed: dict[str, Any] | None = None,
    output: str = "production_bible.json",
    persist: Callable[[dict[str, Any], str], None],
    input_fn: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    """Run the 5-stage interactive wizard. Returns the built bible dict.

    ``input_fn`` is injectable for tests (defaults to stdin ``input``).
    ``persist(bible, output)`` writes file + project state (owned by caller).
    """
    read = input_fn or _prompt_line
    answers: dict[str, Any] = dict(seed or {})
    index = 0
    n = len(STAGES)

    console.print(
        Panel(
            "Guided Production Bible Wizard\n"
            "Enter accepts default · [b]ack · [q]uit",
            title="create-bible --wizard",
            border_style="cyan",
        )
    )

    while 0 <= index < n:
        stage = STAGES[index]
        stage_num = index + 1
        console.print(
            f"\n[bold cyan]Stage {stage_num}/{n}:[/bold cyan] {stage['title']}"
        )

        if stage["id"] == "review":
            try:
                kwargs = answers_to_kwargs(answers)
            except ValueError as exc:
                console.print(f"[red]Cannot review yet:[/red] {exc}")
                index = max(0, index - 1)
                continue
            console.print("[dim]Preview kwargs → build_production_bible[/dim]")
            console.print(json.dumps(kwargs, indent=2))
            notes = build_notes(answers)
            if notes:
                console.print(Panel(notes, title="Notes rollup", border_style="dim"))
            confirm = read("Generate Production Bible? [Y/n/b/q]: ").strip().lower()
            if confirm in ("q", "quit"):
                console.print("[yellow]Wizard cancelled[/yellow]")
                raise typer.Exit(1)
            if confirm in ("b", "back"):
                index -= 1
                continue
            if confirm in ("", "y", "yes"):
                bible = build_production_bible(**kwargs)
                persist(bible, output)
                return bible
            console.print("[dim]Enter Y to confirm, b to go back, q to quit[/dim]")
            continue

        # Collect fields for this stage
        for field in stage["fields"]:
            key = field["key"]
            current = answers.get(key, field["default"])
            default_hint = "" if current is None or current == "" else f" [{current}]"
            example = field["example"]
            console.print(f"  [dim]e.g. {example}[/dim]")
            while True:
                raw = read(f"  {field['prompt']}{default_hint}: ")
                low = raw.strip().lower()
                if low in ("q", "quit"):
                    console.print("[yellow]Wizard cancelled[/yellow]")
                    raise typer.Exit(1)
                if low in ("b", "back"):
                    # Signal back without consuming remaining fields
                    answers["_nav"] = "back"
                    break
                _apply_field_value(field, raw, answers)
                # Field-level duration check
                if key == "target_duration_seconds":
                    trial = {**answers}
                    if trial.get(key) is None and field["default"] is not None:
                        trial[key] = field["default"]
                    errs = validate_answers(stage["id"], trial)
                    # Only duration-related errors for this field
                    dur_errs = [e for e in errs if "duration" in e.lower()]
                    if dur_errs:
                        for e in dur_errs:
                            console.print(f"  [red]{e}[/red]")
                        continue
                break
            if answers.pop("_nav", None) == "back":
                index = max(0, index - 1)
                break
        else:
            # Completed all fields without back
            errs = validate_answers(stage["id"], answers)
            # Fill defaults for blank required-with-default before validate re-check
            for field in stage["fields"]:
                if field["default"] is not None and (
                    field["key"] not in answers or answers[field["key"]] is None
                ):
                    answers[field["key"]] = field["default"]
            errs = validate_answers(stage["id"], answers)
            if errs:
                for e in errs:
                    console.print(f"[red]{e}[/red]")
                continue  # re-run same stage
            index += 1
            continue
        # broke via back from field loop — index already adjusted
        continue

    console.print("[yellow]Wizard ended without generating a bible[/yellow]")
    raise typer.Exit(1)
