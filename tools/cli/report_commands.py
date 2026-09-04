"""Report and validation CLI commands."""

from __future__ import annotations

from datetime import datetime

import typer

from models import verify_model_compatibility
from project_state import load_project_state
from studio_health import MIN_EXPECTED_SKILLS, count_skills
from studio_paths import AGENTS_DIR, CHARACTERS_DIR, SEQUENCES_DIR, STUDIO_ROOT

from cli.shared import (
    AGENT_ROLE_CARDS,
    EXPECTED_ROLE_CARD_COUNT,
    STUDIO_VERSION,
    console,
    list_role_card_files,
)

SKILLS_ROOT = STUDIO_ROOT / ".grok" / "skills"


def register(app: typer.Typer) -> None:
    @app.command(name="report")
    def report(
        output: str = typer.Option("production_report.pdf", "--output", "-o", help="Output PDF filename"),
    ):
        """Generate a basic PDF production report."""
        try:
            from fpdf import FPDF
        except ImportError:
            console.print("[red]fpdf2 not installed. Run: pip install fpdf2[/red]")
            raise typer.Exit(1)

        state = load_project_state()
        project = state.get("project", {})

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=16)
        pdf.cell(0, 10, "Grok Imagine Cinematic Studio — Production Report", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Helvetica", size=12)
        project_title = project.get("project_title") or project.get("title", "Untitled")
        pdf.cell(0, 8, f"Project: {project_title}", ln=True)
        pdf.cell(0, 8, f"Genre: {project.get('genre', 'N/A')}", ln=True)
        pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
        pdf.ln(5)
        pdf.cell(
            0,
            8,
            f"Status: Production in progress — studio v{STUDIO_VERSION} · Grok 4.6 · 25-agent core",
            ln=True,
        )

        pdf.output(output)
        console.print(f"[green]✅ PDF Report generated:[/green] {output}")

    @app.command(name="validate")
    def validate():
        """Run local validation — docs, skills, models, and workspace paths."""
        console.print("[bold]🔍 Running local validation...[/bold]\n")

        issues = 0

        if not AGENTS_DIR.exists():
            console.print("[red]❌ references/agents/ directory missing[/red]")
            issues += 1
        else:
            cards = list_role_card_files()
            card_count = len(cards)
            console.print(f"[green]✅ Found {card_count} Role Cards in references/agents/[/green]")
            if card_count != EXPECTED_ROLE_CARD_COUNT:
                console.print(
                    f"[yellow]⚠️  Expected {EXPECTED_ROLE_CARD_COUNT} role cards, found {card_count}[/yellow]"
                )
                issues += 1
            missing = [
                name for name, rel in AGENT_ROLE_CARDS.items()
                if not (AGENTS_DIR / rel).is_file()
            ]
            if missing:
                console.print(f"[red]❌ Missing role cards for {len(missing)} agent(s)[/red]")
                for name in missing[:5]:
                    console.print(f"  [red]• {name}[/red]")
                issues += 1

        core_files = ["MASTER_PROMPT.md", "README.md", "docs/guides/Quick_Start_Guide.md"]
        for f in core_files:
            if (STUDIO_ROOT / f).exists():
                console.print(f"[green]✅ {f} present[/green]")
            else:
                console.print(f"[yellow]⚠️  {f} missing[/yellow]")
                issues += 1

        if SKILLS_ROOT.is_dir():
            skill_count = count_skills()
            console.print(f"[green]✅ Found {skill_count} skills in .grok/skills/[/green]")
            if skill_count < MIN_EXPECTED_SKILLS:
                console.print(f"[yellow]⚠️  Expected ≥{MIN_EXPECTED_SKILLS} skills, found {skill_count}[/yellow]")
                issues += 1
        else:
            console.print("[red]❌ .grok/skills/ directory missing[/red]")
            issues += 1

        for label, path in (
            ("characters/", CHARACTERS_DIR),
            ("sequences/", SEQUENCES_DIR),
        ):
            if path.exists():
                console.print(f"[green]✅ {label} directory present[/green]")
            else:
                console.print(f"[yellow]⚠️  {label} directory missing (will be created on first use)[/yellow]")

        model_result = verify_model_compatibility()
        if model_result["compatible"]:
            stack = model_result.get("model_stack") or {}
            console.print(
                "[green]✅ Model stack compatible[/green] "
                f"(chat [bold]{stack.get('xai_chat', 'grok-4.6')}[/bold] · "
                f"video {stack.get('imagine_video', 'grok-imagine-video')} · "
                f"Grok 4.6 · v{STUDIO_VERSION})"
            )
            for warn in model_result.get("warnings") or []:
                console.print(f"  [yellow]• {warn}[/yellow]")
        else:
            console.print("[red]❌ Model compatibility issues[/red]")
            for issue in model_result["issues"]:
                console.print(f"  [red]• {issue}[/red]")
            issues += 1

        if issues == 0:
            console.print(
                f"\n[bold green]✅ Validation passed (v{STUDIO_VERSION} · Grok 4.6)[/bold green]"
            )
        else:
            console.print(f"\n[yellow]Validation completed with {issues} issue(s)[/yellow]")
            raise typer.Exit(1)