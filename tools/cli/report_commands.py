"""Report and validation CLI commands."""

from __future__ import annotations

from datetime import datetime

import typer

from models import verify_model_compatibility
from project_state import load_project_state
from studio_paths import AGENTS_DIR, CHARACTERS_DIR, SEQUENCES_DIR, STUDIO_ROOT

from cli.shared import STUDIO_VERSION, console

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
        pdf.cell(0, 8, "Status: Production in progress with 23-agent studio", ln=True)

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
            card_count = len(list(AGENTS_DIR.glob("*.md")))
            console.print(f"[green]✅ Found {card_count} Role Cards in references/agents/[/green]")

        core_files = ["MASTER_PROMPT_v3.6.md", "README.md", "Quick_Start_Guide.md"]
        for f in core_files:
            if (STUDIO_ROOT / f).exists():
                console.print(f"[green]✅ {f} present[/green]")
            else:
                console.print(f"[yellow]⚠️  {f} missing[/yellow]")
                issues += 1

        if SKILLS_ROOT.is_dir():
            skill_count = sum(1 for d in SKILLS_ROOT.iterdir() if (d / "SKILL.md").is_file())
            console.print(f"[green]✅ Found {skill_count} skills in .grok/skills/[/green]")
            if skill_count < 25:
                console.print(f"[yellow]⚠️  Expected ~30 skills, found {skill_count}[/yellow]")
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
            console.print("[green]✅ Model stack compatible[/green]")
        else:
            console.print("[red]❌ Model compatibility issues[/red]")
            for issue in model_result["issues"]:
                console.print(f"  [red]• {issue}[/red]")
            issues += 1

        if issues == 0:
            console.print(f"\n[bold green]✅ Validation passed (v{STUDIO_VERSION})[/bold green]")
        else:
            console.print(f"\n[yellow]Validation completed with {issues} issue(s)[/yellow]")
            raise typer.Exit(1)