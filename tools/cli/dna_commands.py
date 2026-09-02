"""Character DNA CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from character_dna import (
    PROMPT_MODES,
    build_handoff_packet,
    build_prompt_blocks,
    create_dna_scaffold,
    inject_into_prompt,
    list_characters,
    load_character_dna,
    lock_to_identity_bank,
    save_character_dna,
)

from cli.helpers import require_character_dna, require_character_dna_path
from cli.shared import console

def register(app: typer.Typer) -> None:
    @app.command("init")
    def dna_init(
        name: str = typer.Argument(..., help="Character name"),
        core_identity: str = typer.Option("", "--core", help="Core identity description"),
        facial_dna: str = typer.Option("", "--facial", help="Facial DNA description"),
        hair: str = typer.Option("", "--hair", help="Hair & grooming"),
        clothing: str = typer.Option("", "--clothing", help="Clothing & style"),
        movement: str = typer.Option("", "--movement", help="Movement & posture"),
        emotion: str = typer.Option("", "--emotion", help="Emotional baseline"),
        motion: str = typer.Option("", "--motion", help="Motion DNA for video"),
        anchor: list[str] = typer.Option(None, "--anchor", help="Key consistency anchor (repeatable)"),
        subject_kind: str = typer.Option(
            "unspecified",
            "--subject-kind",
            help="unspecified | imaginary_adult | real_person (intimate DNA requires imaginary_adult)",
        ),
        output: str = typer.Option(None, "--output", "-o", help="Output dna.json path"),
    ):
        """Create a new Character DNA profile scaffold."""
        dna = create_dna_scaffold(
            name,
            core_identity=core_identity,
            facial_dna=facial_dna,
            hair_grooming=hair,
            clothing_style=clothing,
            movement_posture=movement,
            emotional_baseline=emotion,
            motion_dna=motion,
            key_anchors=anchor or [],
            source="cli-init",
            subject_kind=subject_kind,
        )
        if output:
            out_path = Path(output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(dna, indent=2))
            console.print(f"[green]✅ DNA scaffold created:[/green] {out_path}")
        else:
            json_path, md_path = save_character_dna(dna)
            console.print(f"[green]✅ DNA scaffold created:[/green]")
            console.print(f"  JSON: {json_path}")
            console.print(f"  Markdown: {md_path}")
        console.print("[dim]Edit the profile, then run: dna lock --name \"{name}\"[/dim]".format(name=name))

    @app.command("save")
    def dna_save(
        file: Path = typer.Option(..., "--file", "-f", help="Path to dna.json to validate and persist"),
    ):
        """Validate and save a Character DNA profile to characters/{slug}/."""
        dna = load_character_dna(file)
        try:
            json_path, md_path = save_character_dna(dna)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        console.print(f"[green]✅ DNA saved:[/green] {json_path}")
        console.print(f"[dim]Markdown:[/dim] {md_path}")

    @app.command("list")
    def dna_list():
        """List all Character DNA profiles."""
        chars = list_characters()
        if not chars:
            console.print("[yellow]No Character DNA profiles yet. Run: dna init \"Character Name\"[/yellow]")
            return
        table = Table(title="🧬 Character DNA Profiles", box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Slug", style="dim")
        table.add_column("Version", style="white")
        table.add_column("Lock Status", style="green")
        for c in chars:
            table.add_row(c["name"], c["slug"], str(c["version"]), c["status"])
        console.print(table)

    @app.command("show")
    def dna_show(
        name: str = typer.Argument(..., help="Character name or slug"),
        mode: str = typer.Option(None, "--mode", "-m", help="Show prompt injection for mode"),
    ):
        """Display a Character DNA profile or prompt injection block."""
        dna = require_character_dna(name)
        if mode:
            if mode not in PROMPT_MODES:
                console.print(f"[red]Unknown mode. Choose from:[/red] {', '.join(PROMPT_MODES)}")
                raise typer.Exit(1)
            blocks = build_prompt_blocks(dna)
            console.print(Panel(blocks[mode], title=f"Prompt Injection — {mode}", border_style="green"))
        else:
            from character_dna import dna_to_markdown
            console.print(Panel(Markdown(dna_to_markdown(dna)[:4000]), title=f"🧬 {dna['character_name']}", border_style="blue"))

    @app.command("handoff")
    def dna_handoff(
        name: str = typer.Argument(..., help="Character name or slug"),
        output: str = typer.Option(None, "--output", "-o", help="Output handoff.json path"),
    ):
        """Generate Identity Lock handoff packet from DNA profile."""
        dna_path = require_character_dna_path(name)
        dna = require_character_dna(name)
        handoff = build_handoff_packet(dna)
        out_path = Path(output) if output else dna_path.parent / "handoff.json"
        out_path.write_text(json.dumps(handoff, indent=2))
        console.print(f"[green]✅ Handoff packet created:[/green] {out_path}")
        console.print("[dim]Next: dna lock --name \"{name}\"[/dim]".format(name=dna["character_name"]))

    @app.command("lock")
    def dna_lock(
        name: str = typer.Argument(..., help="Character name or slug"),
    ):
        """Import DNA into Identity Lock memory bank."""
        dna = require_character_dna(name)
        try:
            state = lock_to_identity_bank(dna)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        console.print(f"[green]✅ Identity Lock engaged for[/green] {dna['character_name']}")
        console.print(f"[dim]Status: locked | Drift threshold: 2.5 | Anchors: {len(dna.get('key_consistency_anchors', []))}[/dim]")
        console.print(f"[dim]Identity Lock entries: {len(state.get('identity_lock', {}))}[/dim]")

    @app.command("inject")
    def dna_inject(
        name: str = typer.Argument(..., help="Character name or slug"),
        mode: str = typer.Option("cinematic", "--mode", "-m", help="Injection mode"),
        base_prompt: str = typer.Option("", "--base", "-b", help="Base prompt to prepend injection onto"),
        output: str = typer.Option(None, "--output", "-o", help="Save injected prompt to file"),
    ):
        """Generate CHARACTER_DNA prompt injection for Imagine Prompt Master."""
        try:
            result = inject_into_prompt(base_prompt, name, mode)
        except FileNotFoundError:
            console.print(f"[red]No DNA profile found for:[/red] {name}")
            raise typer.Exit(1)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1)
        if output:
            Path(output).write_text(result)
            console.print(f"[green]✅ Injected prompt saved:[/green] {output}")
        else:
            console.print(Panel(result, title=f"Prompt Injection — {mode}", border_style="green"))
