"""Register cinematic-studio api (FastAPI control plane)."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from cli.shared import console


def register(app: typer.Typer) -> None:
    @app.command("api")
    def api(
        host: str = typer.Option(
            "127.0.0.1",
            "--host",
            help="Bind host (use 0.0.0.0 for LAN)",
        ),
        port: int = typer.Option(
            8090,
            "--port",
            "-p",
            help="Bind port (default 8090)",
            min=1,
            max=65535,
        ),
        reload: bool = typer.Option(
            False,
            "--reload",
            help="Auto-reload on code changes (dev only)",
        ),
    ) -> None:
        """Launch the FastAPI control plane (dashboard + ActionSpec execute).

        Requires: pip install -r requirements-api.txt

        Endpoints:
          GET  /health
          GET  /v1/dashboard
          GET  /v1/actions
          GET  /v1/actions/{id}
          POST /v1/actions/{id}/execute
        """
        try:
            import fastapi  # noqa: F401
            import uvicorn  # noqa: F401
        except ImportError as exc:
            py = sys.executable
            console.print(
                "[red]FastAPI/uvicorn not installed.[/red]\n"
                f"  [bold]{py} -m pip install -r requirements-api.txt[/bold]"
            )
            raise typer.Exit(1) from exc

        root = Path(__file__).resolve().parents[2]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))

        from studio_api.app import run_api

        console.print(
            f"[cyan]Studio API[/cyan] → http://{host}:{port}/\n"
            "[dim]GET /v1/dashboard · GET /v1/actions · "
            "POST /v1/actions/{id}/execute · core: studio_core[/dim]"
        )
        run_api(host=host, port=port, reload=reload)
