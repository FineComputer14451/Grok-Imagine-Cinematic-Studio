"""Register cinematic-studio ui (Textual TUI)."""

from __future__ import annotations

import sys

import typer

from cli.shared import console


def register(app: typer.Typer) -> None:
    @app.command("ui")
    def ui(
        interval: float = typer.Option(
            5.0,
            "--interval",
            "-i",
            help="Home auto-refresh seconds (min 1.0)",
            min=1.0,
        ),
    ) -> None:
        """Interactive terminal UI — live studio dashboard + command launcher."""
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            console.print(
                "[red]cinematic-studio ui requires an interactive terminal.[/red]"
            )
            raise typer.Exit(1)
        try:
            import textual  # noqa: F401
        except ImportError as exc:
            console.print(
                "[red]Textual is required for the TUI.[/red]\n"
                "Install with: [bold]pip install 'textual>=0.47.0'[/bold] "
                "(or pip install -r requirements.txt)"
            )
            raise typer.Exit(1) from exc

        from cli.tui.app import run_tui

        run_tui(interval=interval)
