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
from plugin_catalog import (
    catalog_pinned_sha,
    check_plugin_artifacts,
    discover_commands,
    discover_skills,
    git_head_sha,
    sync_marketplace_sha,
    write_artifacts,
)
from plugin_packs import (
    PACK_IDS,
    load_plugin_packs,
    validate_plugin_packs,
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
        False,
        "--release",
        help=(
            "Require a valid release pin: install SHA is HEAD, or an ancestor "
            "with only .grok-plugin catalog files after it (pre-publish gate)"
        ),
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
            pin = catalog_pinned_sha(marketplace) or "?"
            head = git_head_sha()
            if pin == head:
                pin_line = f"install SHA == HEAD ({pin[:12]}…)"
            else:
                pin_line = (
                    f"install SHA {pin[:12]}… (content revision); "
                    f"HEAD {head[:12]}… is pin-only catalog follow-up"
                )
            console.print(Panel.fit(
                "[bold green]✅ Release pin verified[/bold green]\n\n"
                f"{pin_line}\n"
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
        console.print(
            "\n[yellow]Workflow: commit content first → "
            "`plugin catalog pin` → commit only `.grok-plugin/` → "
            "`plugin catalog check --release`.[/yellow]"
        )
    raise typer.Exit(1)


@catalog_app.command("pin")
def catalog_pin():
    """Pin the marketplace install SHA to current HEAD and write fresh artifacts.

    Commit content first, then pin, then commit **only** ``.grok-plugin/`` so
    the install SHA stays on the content revision (a commit cannot embed its
    own hash in marketplace.json).
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
        console.print(f"[green]Pinned marketplace install SHA to {head}[/green]")

    console.print(
        f"[green]✅ Wrote plugin artifacts "
        f"({result.get('skills', 0)} skills, {result.get('commands', 0)} commands)[/green]"
    )
    console.print(
        "[dim]Next: git add .grok-plugin/ && commit (catalog files only). "
        "Then: plugin catalog check --release[/dim]"
    )


@plugin_app.command("packs")
def plugin_packs(
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Dump raw plugin_packs.yaml config as JSON",
    ),
):
    """List modular plugin packs and the full-suite plugin name."""
    try:
        cfg = load_plugin_packs()
    except Exception as e:
        console.print(f"[red]ERROR: cannot load plugin packs: {e}[/red]")
        raise typer.Exit(1)

    errors = validate_plugin_packs(cfg)
    if errors:
        console.print("[bold red]❌ Plugin pack config invalid[/bold red]")
        for err in errors:
            console.print(f"  [red]• {err}[/red]")
        raise typer.Exit(1)

    if json_output:
        print(json.dumps(cfg, indent=2))
        return

    full = cfg.get("full_plugin") or {}
    full_name = full.get("name") or "?"
    full_display = full.get("display_name") or full_name
    console.print(f"[bold]Full suite:[/bold] {full_name}")
    if full_display and full_display != full_name:
        console.print(f"  [dim]{full_display}[/dim]")
    console.print()

    packs = cfg.get("packs") or {}
    table = Table(title="Plugin Packs", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Skills", justify="right")
    table.add_column("Commands", justify="right")
    table.add_column("Requires", style="yellow")

    for pid in PACK_IDS:
        pack = packs.get(pid) or {}
        skills = pack.get("skills") or []
        commands = pack.get("commands") or []
        requires = pack.get("requires") or []
        req_str = ", ".join(requires) if requires else "—"
        table.add_row(
            pid,
            pack.get("name") or "?",
            str(len(skills)),
            str(len(commands)),
            req_str,
        )

    console.print(table)


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
def plugin_list(
    grouped: bool = typer.Option(
        False,
        "--grouped",
        "-g",
        help="Group skills by production department (taxonomy)",
    ),
):
    """List skills and commands that would be published in the plugin index."""
    skills = discover_skills()
    commands = discover_commands()

    if grouped:
        from plugin_catalog import skill_taxonomy_groups

        groups = skill_taxonomy_groups([s["name"] for s in skills])
        console.print(f"[bold]{len(skills)} skills[/bold] (grouped)\n")
        for group_name, names in groups.items():
            if not names:
                continue
            console.print(f"[cyan]{group_name}[/cyan] ({len(names)})")
            for name in names:
                console.print(f"  • {name}")
            console.print()
    else:
        console.print(f"[bold]{len(skills)} skills[/bold]")
        for s in skills:
            console.print(f"  • {s['name']}")

    if commands:
        console.print(f"\n[bold]{len(commands)} commands[/bold]")
        for c in commands:
            console.print(f"  • {c['name']}")


@plugin_app.command("declutter")
def plugin_declutter(
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Actually remove duplicates (default is dry-run)",
    ),
    keep_backups: int = typer.Option(
        1,
        "--keep-backups",
        help="Number of newest ~/.grok/skills-backup-* dirs to keep",
    ),
    keep_skills_copy: bool = typer.Option(
        False,
        "--keep-skills-copy",
        help="Do not remove studio skills from ~/.grok/skills/",
    ),
):
    """Declutter dual Method A+B installs (delegates to cinematic_studio.sh).

    When the Grok plugin is installed, studio skills under ~/.grok/skills/ are
    redundant and triple-load in Grok Build. This removes those copies and
    prunes old Method A update backups.
    """
    import subprocess
    from pathlib import Path

    script = Path(__file__).resolve().parents[2] / "scripts" / "cinematic_studio.sh"
    if not script.is_file():
        console.print(f"[red]Missing installer script: {script}[/red]")
        raise typer.Exit(1)

    cmd = ["bash", str(script), "declutter"]
    if apply:
        cmd.append("--apply")
    else:
        cmd.append("--dry-run")
    cmd.extend(["--keep-backups", str(keep_backups)])
    if keep_skills_copy:
        cmd.append("--keep-skills-copy")

    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        raise typer.Exit(result.returncode)


def register(app: typer.Typer) -> None:
    """Register the plugin subcommand group on the root CLI."""
    app.add_typer(plugin_app, name="plugin")


# For standalone use if someone imports the app directly
if __name__ == "__main__":
    # Support direct `python -m tools.cli.plugin_commands` for debugging
    plugin_app()
