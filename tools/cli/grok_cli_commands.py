"""Grok Build CLI binary management — ensure / update / status."""

from __future__ import annotations

import json

import typer
from rich.panel import Panel
from rich.table import Table

from grok_build_cli import (
    OFFICIAL_INSTALL_URL,
    ensure_via_bash_lib,
    ensure_grok_build_cli,
    probe_preferred,
    run_grok_update,
    run_official_installer,
)
from models import RECOMMENDED_GROK_BUILD_CLI_VERSION

from cli.shared import console


def register(app: typer.Typer) -> None:
    grok_app = typer.Typer(
        help=(
            "Grok Build CLI binary (install / update / ensure ≥ "
            f"{RECOMMENDED_GROK_BUILD_CLI_VERSION})"
        )
    )
    app.add_typer(grok_app, name="grok")

    @grok_app.command("status")
    def status(
        json_out: bool = typer.Option(False, "--json", help="Machine-readable JSON"),
    ):
        """Show Grok Build binary path, version, and min requirement."""
        probe = probe_preferred()
        if json_out:
            console.print_json(data=probe)
            return
        table = Table(title="Grok Build CLI", show_header=False, box=None)
        table.add_column("k", style="cyan")
        table.add_column("v")
        table.add_row("path", str(probe.get("path") or "— not found —"))
        table.add_row("version", str(probe.get("version") or "—"))
        table.add_row("display", str(probe.get("display") or "—"))
        table.add_row("min recommended", str(probe.get("min_version")))
        table.add_row(
            "meets min",
            "[green]yes[/green]" if probe.get("meets_min") else "[red]no[/red]",
        )
        console.print(table)
        if not probe.get("path"):
            console.print(
                "\n[yellow]Install:[/yellow] "
                f"[dim]cinematic-studio grok ensure[/dim]  or  "
                f"curl -fsSL {OFFICIAL_INSTALL_URL} | bash"
            )
        elif not probe.get("meets_min"):
            console.print(
                "\n[yellow]Upgrade:[/yellow] "
                "[dim]cinematic-studio grok update[/dim]  or  "
                "[dim]cinematic-studio grok ensure --force[/dim]"
            )

    @grok_app.command("ensure")
    def ensure(
        force: bool = typer.Option(
            False,
            "--force",
            "-f",
            help="Refresh even if min version is already met",
        ),
        python_only: bool = typer.Option(
            False,
            "--python-only",
            help="Use pure-Python path (skip bash install_cli_wrappers.sh)",
        ),
        json_out: bool = typer.Option(False, "--json"),
    ):
        """
        Ensure Grok Build CLI binary is installed and ≥ recommended min.

        Same policy as Method A install (scripts/lib/install_cli_wrappers.sh):
        prefer `grok update --stable`, else official x.ai installer.
        """
        if python_only:
            result = ensure_grok_build_cli(force=force)
        else:
            result = ensure_via_bash_lib(force=force)
        if json_out:
            # probe may not be JSON-serializable Path-free already
            console.print(json.dumps(result, indent=2, default=str))
        else:
            probe = result.get("probe") or {}
            body = (
                f"[bold]{result.get('message')}[/bold]\n"
                f"path: {probe.get('path') or '—'}\n"
                f"version: {probe.get('version') or '—'}\n"
                f"backend: {result.get('backend', 'python')}\n"
            )
            if result.get("steps"):
                body += "steps: " + " → ".join(str(s) for s in result["steps"]) + "\n"
            if result.get("detail"):
                # keep short
                tail = str(result["detail"])[-500:]
                body += f"\n[dim]{tail}[/dim]"
            style = "green" if result.get("ok") else "yellow"
            console.print(Panel(body, title="Grok Build CLI ensure", border_style=style))
        if not result.get("ok") and not result.get("skipped"):
            raise typer.Exit(1)

    @grok_app.command("update")
    def update(
        force_install: bool = typer.Option(
            False,
            "--force-install",
            help="If update fails, run official installer",
        ),
        json_out: bool = typer.Option(False, "--json"),
    ):
        """Run `grok update --stable` (or ensure if missing)."""
        probe = probe_preferred()
        if not probe.get("path"):
            console.print("[yellow]No grok binary — running ensure…[/yellow]")
            result = ensure_via_bash_lib(force=True)
        else:
            result = run_grok_update(stable=True)
            if force_install and (
                not result.get("ok")
                or not (result.get("probe") or {}).get("meets_min")
            ):
                console.print("[yellow]Update incomplete — running official installer…[/yellow]")
                result = run_official_installer()
        if json_out:
            console.print(json.dumps(result, indent=2, default=str))
        else:
            probe = result.get("probe") or probe_preferred()
            console.print(
                Panel(
                    f"{result.get('message')}\n"
                    f"path: {probe.get('path') or '—'}\n"
                    f"version: {probe.get('version') or '—'}",
                    title="Grok Build CLI update",
                    border_style="green" if result.get("ok") else "yellow",
                )
            )
            if result.get("detail"):
                console.print(f"[dim]{str(result['detail'])[-800:]}[/dim]")
        if not result.get("ok"):
            raise typer.Exit(1)

    @grok_app.command("install")
    def install(
        json_out: bool = typer.Option(False, "--json"),
    ):
        """Force official installer from https://x.ai/cli/install.sh (or CINEMATIC_GROK_INSTALL_URL)."""
        result = run_official_installer()
        if json_out:
            console.print(json.dumps(result, indent=2, default=str))
        else:
            probe = result.get("probe") or probe_preferred()
            console.print(
                Panel(
                    f"{result.get('message')}\n"
                    f"path: {probe.get('path') or '—'}\n"
                    f"version: {probe.get('version') or '—'}\n"
                    f"url: {OFFICIAL_INSTALL_URL}",
                    title="Grok Build CLI install",
                    border_style="green" if result.get("ok") else "yellow",
                )
            )
            if result.get("detail"):
                console.print(f"[dim]{str(result['detail'])[-800:]}[/dim]")
        if not result.get("ok"):
            raise typer.Exit(1)
