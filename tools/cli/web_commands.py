"""Register cinematic-studio web (NiceGUI shell)."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from cli.shared import console


def register(app: typer.Typer) -> None:
    @app.command("web")
    def web(
        host: str = typer.Option(
            "127.0.0.1",
            "--host",
            "-h",
            help="Bind host (use 0.0.0.0 for LAN)",
        ),
        port: int = typer.Option(
            8088,
            "--port",
            "-p",
            help="Bind port (default 8088; Streamlit often uses 8501)",
            min=1,
            max=65535,
        ),
        reload: bool = typer.Option(
            False,
            "--reload",
            help="Auto-reload on code changes (dev only)",
        ),
        open_browser: bool = typer.Option(
            False,
            "--open",
            help="Open a browser tab on start",
        ),
    ) -> None:
        """Launch the NiceGUI web shell (dashboard, production, DNA, sequences, imagine, quota).

        Requires: pip install -r requirements-nicegui.txt

        Streamlit remains available via: streamlit run web_ui/app.py
        """
        try:
            import nicegui  # noqa: F401
        except ImportError as exc:
            py = sys.executable
            console.print(
                "[red]NiceGUI is not installed.[/red]\n"
                f"Python: [bold]{py}[/bold]\n"
                "Install:\n"
                f"  [bold]{py} -m pip install -r requirements-nicegui.txt[/bold]\n"
                "or:\n"
                f"  [bold]{py} -m pip install 'nicegui>=2.0.0'[/bold]\n"
                "Streamlit UI (no NiceGUI needed):\n"
                "  [bold]streamlit run web_ui/app.py[/bold]"
            )
            raise typer.Exit(1) from exc

        root = Path(__file__).resolve().parents[2]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))

        try:
            from web_nicegui.app import run_web
        except ImportError as exc:
            console.print(f"[red]Failed to load web_nicegui package:[/red] {exc}")
            raise typer.Exit(1) from exc

        console.print(
            f"[cyan]NiceGUI dashboard[/cyan] → http://{host}:{port}/\n"
            "[dim]Dashboard · Production · DNA · Sequences · Imagine · Quota via execute_action · modes compact/ops/full · "
            "core: studio_core.services.dashboard[/dim]"
        )
        run_web(host=host, port=port, reload=reload, show=open_browser)
