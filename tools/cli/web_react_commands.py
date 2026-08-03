"""Register cinematic-studio web-react (TanStack SPA cockpit)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import typer

from cli.shared import console


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _web_react_dir() -> Path:
    return _repo_root() / "web_react"


def _require_npm() -> str:
    npm = shutil.which("npm")
    if not npm:
        console.print(
            "[red]npm not found on PATH.[/red]\n"
            "Install Node.js 20+ (includes npm), then retry.\n"
            "  https://nodejs.org/  ·  or  [bold]sudo apt install npm[/bold]"
        )
        raise typer.Exit(1)
    node = shutil.which("node")
    if not node:
        console.print("[red]node not found on PATH (npm alone is not enough).[/red]")
        raise typer.Exit(1)
    return npm


def _ensure_deps(npm: str, app_dir: Path, *, force_install: bool) -> None:
    modules = app_dir / "node_modules"
    if modules.is_dir() and not force_install:
        return
    console.print(
        f"[cyan]npm install[/cyan] in {app_dir}"
        + (" (--install)" if force_install else " (node_modules missing)")
    )
    result = subprocess.run(
        [npm, "install"],
        cwd=str(app_dir),
        check=False,
    )
    if result.returncode != 0:
        console.print("[red]npm install failed.[/red]")
        raise typer.Exit(result.returncode or 1)


def register(app: typer.Typer) -> None:
    @app.command("web-react")
    def web_react(
        host: str = typer.Option(
            "127.0.0.1",
            "--host",
            help="Vite bind host (use 0.0.0.0 for LAN)",
        ),
        port: int = typer.Option(
            5173,
            "--port",
            "-p",
            help="Vite port (default 5173)",
            min=1,
            max=65535,
        ),
        api_url: str = typer.Option(
            "",
            "--api-url",
            help=(
                "studio_api base URL (sets VITE_STUDIO_API_URL). "
                "Empty = same-origin; dev/preview proxy /v1 → http://127.0.0.1:8090"
            ),
        ),
        install: bool = typer.Option(
            False,
            "--install",
            help="Force npm install before start",
        ),
        preview: bool = typer.Option(
            False,
            "--preview",
            help="Serve production build (npm run build + preview) instead of dev",
        ),
        open_browser: bool = typer.Option(
            False,
            "--open",
            help="Open a browser tab on start",
        ),
    ) -> None:
        """Launch the React/TanStack cockpit (NiceGUI-parity SPA on FastAPI).

        Requires Node.js 20+ and a running control plane::

            cinematic-studio api --port 8090

        Dev (default)::

            cinematic-studio web-react
            # → http://127.0.0.1:5173  (proxies /v1 and /health → :8090)

        Production-style local serve::

            cinematic-studio web-react --preview --port 4173
        """
        app_dir = _web_react_dir()
        pkg = app_dir / "package.json"
        if not pkg.is_file():
            console.print(
                f"[red]web_react package not found:[/red] {pkg}\n"
                "Clone the full repo or restore the web_react/ tree."
            )
            raise typer.Exit(1)

        npm = _require_npm()
        _ensure_deps(npm, app_dir, force_install=install)

        env = os.environ.copy()
        api = (api_url or "").strip().rstrip("/")
        if api:
            env["VITE_STUDIO_API_URL"] = api

        mode = "preview" if preview else "dev"
        console.print(
            f"[cyan]React/TanStack cockpit[/cyan] ({mode}) → "
            f"http://{host}:{port}/\n"
            "[dim]Routes: / · /production · /dna · /sequences · /imagine · /quota · "
            "core: studio_api → studio_core[/dim]"
        )
        if not api:
            console.print(
                "[dim]API proxy target: http://127.0.0.1:8090 "
                "(start with [bold]cinematic-studio api --port 8090[/bold])[/dim]"
            )
        else:
            console.print(f"[dim]VITE_STUDIO_API_URL={api}[/dim]")

        if preview:
            # Bake env into the client bundle, then serve dist/
            build = subprocess.run(
                [npm, "run", "build"],
                cwd=str(app_dir),
                env=env,
                check=False,
            )
            if build.returncode != 0:
                console.print("[red]npm run build failed.[/red]")
                raise typer.Exit(build.returncode or 1)
            cmd = [
                npm,
                "run",
                "preview",
                "--",
                "--host",
                host,
                "--port",
                str(port),
            ]
        else:
            cmd = [
                npm,
                "run",
                "dev",
                "--",
                "--host",
                host,
                "--port",
                str(port),
            ]

        if open_browser:
            cmd.append("--open")

        # Vite/npm must run with package.json as cwd.
        os.chdir(app_dir)
        try:
            # Replace this process so Ctrl+C reaches Vite cleanly.
            os.execvpe(cmd[0], cmd, env)
        except OSError as exc:
            # Fallback if exec fails (rare on Windows-like envs)
            console.print(f"[yellow]exec failed ({exc}); using subprocess…[/yellow]")
            result = subprocess.run(cmd, cwd=str(app_dir), env=env, check=False)
            raise typer.Exit(result.returncode or 0) from None
        # exec never returns; keep type-checkers happy
        raise typer.Exit(1)  # pragma: no cover
