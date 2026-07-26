"""CLI: handoff packet validate (Operator UX Phase 2 / J4–J5)."""

from __future__ import annotations

from pathlib import Path

import typer

from cli.shared import console


def register(app: typer.Typer) -> None:
    @app.command("validate")
    def handoff_validate(
        path: Path = typer.Argument(..., help="Path to handoff JSON packet"),
        strict_handoff: bool = typer.Option(
            False,
            "--strict-handoff",
            help="Treat readiness blockers as hard failures",
        ),
        strict_wave_a: bool = typer.Option(
            False,
            "--strict-wave-a",
            help="Compose Wave A plate+motion hard path",
        ),
    ) -> None:
        """Validate a handoff JSON packet (schema + soft readiness)."""
        from handoff_validate import format_validation_report, validate_handoff_file

        result = validate_handoff_file(
            path,
            strict_handoff=strict_handoff,
            strict_wave_a=strict_wave_a,
        )
        console.print(format_validation_report(result))
        raise typer.Exit(0 if result.get("ok") else 1)
