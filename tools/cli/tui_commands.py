"""Register cinematic-studio ui (Textual TUI)."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from cli.shared import console


def _print_orient_dashboard(*, write_artifact: bool = True) -> int:
    """TTY-free orient dump (same signals as TUI Home compact)."""
    try:
        from cli.dashboard import build_studio_dashboard
        from cli.tui.widgets import format_orient_brief
    except ImportError as exc:
        console.print(f"[red]Cannot load dashboard formatters:[/red] {exc}")
        return 1

    try:
        snap = build_studio_dashboard()
        try:
            from quota_sync import ledger_recon_alignment

            snap["quota_alignment"] = ledger_recon_alignment()
        except Exception:
            pass
        text = format_orient_brief(snap)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]Dashboard snapshot failed:[/red] {exc}")
        return 1

    console.print(text)
    if write_artifact:
        try:
            from studio_paths import ARTIFACTS_DIR

            ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
            path = ARTIFACTS_DIR / "tui_orient_brief.txt"
            path.write_text(text + "\n", encoding="utf-8")
            console.print(f"\n[dim]Wrote {path}[/dim]")
        except Exception as exc:  # noqa: BLE001
            console.print(f"[dim]Could not write artifact: {exc}[/dim]")
    return 0


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
        print_only: bool = typer.Option(
            False,
            "--print",
            "-p",
            help="Print orient dashboard to stdout (no TTY / no Textual)",
        ),
        no_artifact: bool = typer.Option(
            False,
            "--no-artifact",
            help="With --print, skip writing artifacts/tui_orient_brief.txt",
        ),
    ) -> None:
        """Interactive terminal UI — live studio dashboard + command launcher.

        Without a TTY (agents, pipes, CI): use --print, or bare `ui` falls back
        to a one-shot orient dump instead of failing hard.
        """
        tty = sys.stdin.isatty() and sys.stdout.isatty()

        if print_only or not tty:
            if not print_only and not tty:
                console.print(
                    "[yellow]No interactive TTY — printing orient dashboard "
                    "(full Textual UI needs a real terminal).[/yellow]\n"
                    "[dim]Tip: cinematic-studio ui --print · or run ui in your shell TTY[/dim]\n"
                )
            code = _print_orient_dashboard(write_artifact=not no_artifact)
            raise typer.Exit(code)

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
                "Headless orient dump (no Textual):\n"
                "  [bold]cinematic-studio ui --print[/bold]\n"
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
                "or set [bold]CINEMATIC_PROJECT_DIR[/bold] to a full checkout.\n"
                "Headless: [bold]cinematic-studio ui --print[/bold]"
            )
            raise typer.Exit(1) from exc

        run_tui(interval=interval)
