"""Plugin catalog, manifest, and marketplace release commands.

Integrated into the canonical cinematic-studio CLI as part of the structural
simplification of the plugin tooling (see code-review recommendations).
"""

from __future__ import annotations

import json

import typer
from rich import box
from rich.panel import Panel
from rich.table import Table

from cli.shared import STUDIO_VERSION, console
from tools.plugin_catalog import (
    catalog_pinned_sha,
    check_plugin_artifacts,
    discover_commands,
    discover_skills,
    git_head_sha,
    sync_marketplace_sha,
    write_artifacts,
)
from studio_paths import PLUGIN_MARKETPLACE_PATH

# Re-import paths for clarity
try:
    from studio_paths import (
        PLUGIN_INDEX_PATH,
        PLUGIN_MANIFEST_PATH,
    )
except Exception:
    PLUGIN_INDEX_PATH = None
    PLUGIN_MANIFEST_PATH = None


plugin_app = typer.Typer(
    help="Grok plugin manifest, marketplace catalog pinning, and index tools"
)

catalog_app = typer.Typer(
    help="Marketplace catalog, manifest generation, pinning, and validation"
)
plugin_app.add_typer(catalog_app, name="catalog")


@catalog_app.command("check")
def catalog_check(
    release: bool = typer.Option(
        False, "--release", help="Require marketplace catalog SHA to match current HEAD (pre-publish gate)"
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="Machine readable output"),
):
    """Verify plugin manifest, index freshness, and (optionally) release pin."""
    try:
        marketplace = json.loads(PLUGIN_MARKETPLACE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        console.print(f"[red]ERROR: cannot read marketplace.json: {e}[/red]")
        raise typer.Exit(1)

    errors = check_plugin_artifacts(marketplace, require_release_pin=release)

    if json_output:
        import json as jsonmod
        print(jsonmod.dumps({"ok": len(errors) == 0, "errors": errors, "release": release}, indent=2))
        if errors:
            raise typer.Exit(1)
        return

    if not errors:
        if release:
            console.print(Panel.fit(
                "[bold green]✅ Release pin verified[/bold green]\n\n"
                "marketplace catalog pinned to HEAD\n"
                "plugin.json and plugin-index.json are up to date",
                title="Plugin Catalog Check (--release)",
                border_style="green",
            ))
        else:
            console.print("[green]✅ marketplace.json, plugin.json, and plugin-index.json are up to date[/green]")
        return

    console.print("[bold red]❌ Plugin catalog issues[/bold red]")
    for err in errors:
        console.print(f"  [red]• {err}[/red]")
    if release:
        console.print("\n[yellow]Run the release helper and commit .grok-plugin/ together with feature changes.[/yellow]")
    raise typer.Exit(1)


@catalog_app.command("pin")
def catalog_pin():
    """Pin the marketplace catalog SHA to current HEAD and write fresh artifacts.

    Recommended before an atomic release commit.
    Commit the generated .grok-plugin/ files together with your changes.
    """
    try:
        marketplace = json.loads(PLUGIN_MARKETPLACE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        console.print(f"[red]ERROR reading marketplace: {e}[/red]")
        raise typer.Exit(1)

    try:
        head = git_head_sha()
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    result = write_artifacts(marketplace, sync_sha=True)

    if result.get("pinned"):
        console.print(f"[green]Pinned marketplace sha to {head}[/green]")

    console.print(
        f"[green]✅ Wrote plugin artifacts "
        f"({result.get('skills', 0)} skills, {result.get('commands', 0)} commands)[/green]"
    )
    console.print(
        "\n[yellow]Next: git add .grok-plugin/ and commit together with your feature changes.[/yellow]"
    )


@plugin_app.command("status")
def plugin_status(json_output: bool = typer.Option(False, "--json")):
    """Show quick plugin catalog status (skills/commands count + pinned sha)."""
    try:
        marketplace = json.loads(PLUGIN_MARKETPLACE_PATH.read_text(encoding="utf-8"))
    except Exception:
        marketplace = {}

    skills = discover_skills()
    commands = discover_commands()
    pinned = catalog_pinned_sha(marketplace)

    if json_output:
        import json as jsonmod
        print(jsonmod.dumps({
            "version": STUDIO_VERSION,
            "skills": len(skills),
            "commands": len(commands),
            "pinned_sha": pinned,
        }, indent=2))
        return

    table = Table(title="🔌 Plugin Catalog Status", box=box.ROUNDED)
    table.add_column("Item", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Skills", str(len(skills)))
    table.add_row("Commands", str(len(commands)))
    table.add_row("Catalog SHA", pinned or "[yellow]not pinned[/yellow]")
    table.add_row("Studio", f"v{STUDIO_VERSION}")

    console.print(table)
    console.print("\n[dim]Use 'cinematic-studio plugin catalog check' for full validation.[/dim]")


@plugin_app.command("list")
def plugin_list():
    """List skills and commands that would be published in the plugin index."""
    skills = discover_skills()
    commands = discover_commands()

    console.print(f"[bold]{len(skills)} skills[/bold]")
    for s in skills[:10]:
        console.print(f"  • {s['name']}")
    if len(skills) > 10:
        console.print(f"  ... +{len(skills)-10} more")

    if commands:
        console.print(f"\n[bold]{len(commands)} commands[/bold]")
        for c in commands[:8]:
            console.print(f"  • {c['name']}")
        if len(commands) > 8:
            console.print(f"  ... +{len(commands)-8} more")


def register(app: typer.Typer) -> None:
    """Register the plugin subcommand group on the root CLI."""
    app.add_typer(plugin_app, name="plugin")


# For standalone use if someone imports the app directly
if __name__ == "__main__":
    # Support direct `python -m tools.cli.plugin_commands` for debugging
    plugin_app()
