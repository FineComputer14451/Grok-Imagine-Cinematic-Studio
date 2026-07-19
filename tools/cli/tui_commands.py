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
            py = sys.executable
            console.print(
                "[red]Textual is required for the TUI.[/red]\n"
                f"Python in use: [bold]{py}[/bold]\n"
                "Install with:\n"
                f"  [bold]{py} -m pip install 'textual>=0.47.0'[/bold]\n"
                "or (project venv):\n"
                "  [bold]pip install -r requirements.txt[/bold]\n"
                "Then re-run: [bold]cinematic-studio ui[/bold]"
            )
            raise typer.Exit(1) from exc

        try:
            from cli.tui.app import run_tui
        except ImportError as exc:
            console.print(
                "[red]Failed to load the studio TUI package.[/red]\n"
                f"{exc}\n"
                "Re-install/update tools: [bold]cinematic-studio update[/bold] "
                "or set [bold]CINEMATIC_PROJECT_DIR[/bold] to a full checkout."
            )
            raise typer.Exit(1) from exc

        run_tui(interval=interval)
