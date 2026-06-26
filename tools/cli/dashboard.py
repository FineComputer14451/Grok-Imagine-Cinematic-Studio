"""Studio dashboard data aggregation and Rich rendering."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from rich import box
from rich.columns import Columns
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from character_dna import list_characters
from models import model_stack_summary, verify_model_compatibility
from nsfw_orchestrator import list_batches
from project_state import load_project_state
from quota_optimizer import assess_budget_risk, quota_dashboard
from sequence_chain import list_sequences
from studio_health import count_skills

from cli.quota_display import RISK_COLORS
from cli.shared import (
    EXPECTED_ROLE_CARD_COUNT,
    STUDIO_VERSION,
    console,
    core_agent_count,
    list_role_card_files,
    total_agent_count,
)

CHAIN_QA_COLORS = {
    "go": "green",
    "conditional": "yellow",
    "at_risk": "orange1",
    "no_go": "red",
    "pending": "dim",
}
LOCK_COLORS = {"locked": "green", "pending": "yellow"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_studio_dashboard() -> dict[str, Any]:
    """Aggregate studio snapshot for CLI dashboard or JSON export."""
    state = load_project_state()
    project = state.get("project") or {}
    dash = quota_dashboard(state)
    model_check = verify_model_compatibility()
    sequences = list_sequences()
    characters = list_characters()
    batches = list_batches()
    role_cards = list_role_card_files()
    identity_locked = sum(1 for c in characters if c.get("status") == "locked")

    remaining = dash.get("budget_remaining")
    spent = dash.get("session_spent", 0)
    risk = assess_budget_risk(
        {"credits_low": spent, "credits_high": spent},
        tier=dash.get("tier", "supergrok_pro"),
        budget_remaining=remaining,
    )

    title = project.get("project_title") or project.get("title") or "Untitled"
    return {
        "generated_at": _now_iso(),
        "studio_version": STUDIO_VERSION,
        "project": {
            "title": title,
            "genre": project.get("genre"),
            "has_bible": bool(project),
        },
        "studio": {
            "core_agents": core_agent_count(),
            "total_agents": total_agent_count(),
            "role_cards": len(role_cards),
            "role_cards_expected": EXPECTED_ROLE_CARD_COUNT,
            "skills": count_skills(),
            "models_compatible": model_check["compatible"],
            "model_issues": model_check.get("issues", []),
            "model_stack": model_check.get("model_stack", model_stack_summary()),
        },
        "quota": {**dash, "risk_level": risk.get("risk_level", "unknown")},
        "production": {
            "sequences": len(sequences),
            "characters": len(characters),
            "identity_locked": identity_locked,
            "nsfw_batches": len(batches),
        },
        "sequences": sequences[:8],
        "characters": characters[:8],
        "nsfw_batches": batches[:5],
    }


def _risk_text(level: str) -> Text:
    color = RISK_COLORS.get(level, "white")
    return Text(level, style=color)


def _chain_qa_text(status: str) -> Text:
    color = CHAIN_QA_COLORS.get(status, "white")
    return Text(status, style=color)


def _header_panel(snapshot: dict[str, Any]) -> Panel:
    project = snapshot["project"]
    title = project["title"]
    genre = project.get("genre") or "—"
    lines = [
        f"[bold cyan]🎥 Grok Imagine Cinematic Studio v{snapshot['studio_version']}[/bold cyan]",
        f"[dim]{snapshot['generated_at']}[/dim]",
        "",
        f"[bold]Project:[/bold] {title}",
        f"[bold]Genre:[/bold] {genre}",
        f"[bold]Bible:[/bold] {'loaded' if project['has_bible'] else 'not started'}",
    ]
    return Panel("\n".join(lines), title="Studio Dashboard", border_style="cyan", box=box.ROUNDED)


def _studio_health_table(snapshot: dict[str, Any]) -> Table:
    studio = snapshot["studio"]
    table = Table(title="🏥 Studio Health", box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    table.add_row("Agents", f"{studio['core_agents']} core · {studio['total_agents']} total")
    cards = studio["role_cards"]
    card_note = f"{cards}/{studio['role_cards_expected']}"
    if cards != studio["role_cards_expected"]:
        card_note = f"[yellow]{card_note}[/yellow]"
    table.add_row("Role Cards", card_note)
    table.add_row("Skills", str(studio["skills"]))
    models = "[green]compatible[/green]" if studio["models_compatible"] else "[red]issues[/red]"
    table.add_row("Models", models)
    stack = studio["model_stack"]
    table.add_row("Video", stack.get("imagine_video", "—"))
    table.add_row("Image", stack.get("imagine_image", "—"))
    return table


def _quota_table(snapshot: dict[str, Any]) -> Table:
    quota = snapshot["quota"]
    table = Table(title="💰 Quota", box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    table.add_row("Tier", quota.get("tier_label", quota.get("tier", "—")))
    table.add_row("Session Spent", f"{quota.get('session_spent', 0)} credits")
    table.add_row("Generations", str(quota.get("session_generations", 0)))
    remaining = quota.get("budget_remaining")
    if remaining is not None:
        table.add_row("Budget Left", f"{remaining} credits")
    pct = quota.get("budget_pct_used")
    if pct is not None:
        table.add_row("Session %", f"{pct}%")
    daily = quota.get("daily_soft_cap")
    if daily:
        table.add_row("Daily Soft Cap", f"{daily} credits")
    table.add_row("Risk", _risk_text(quota.get("risk_level", "unknown")))
    return table


def _production_summary(snapshot: dict[str, Any]) -> Table:
    prod = snapshot["production"]
    table = Table(title="🎬 Production Assets", box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("Asset", style="cyan")
    table.add_column("Count", justify="right")
    table.add_row("Sequences", str(prod["sequences"]))
    table.add_row("DNA Profiles", str(prod["characters"]))
    table.add_row("Identity Locked", str(prod["identity_locked"]))
    table.add_row("NSFW Batches", str(prod["nsfw_batches"]))
    return table


def _sequences_table(snapshot: dict[str, Any]) -> Table | Text:
    rows = snapshot["sequences"]
    if not rows:
        return Text("No sequences — run: sequence init \"Name\"", style="dim")
    table = Table(title="🎞 Sequences", box=box.SIMPLE, expand=True)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Clips", justify="right")
    table.add_column("Target", justify="right")
    table.add_column("Health", justify="right")
    table.add_column("Chain QA")
    for s in rows:
        table.add_row(
            s["name"][:36],
            str(s["clips"]),
            f"{s['target_duration']}s",
            str(s.get("health") or "—"),
            _chain_qa_text(s.get("chain_qa_status", "pending")),
        )
    total = snapshot["production"]["sequences"]
    if total > len(rows):
        table.caption = f"Showing {len(rows)} of {total}"
    return table


def _characters_table(snapshot: dict[str, Any]) -> Table | Text:
    rows = snapshot["characters"]
    if not rows:
        return Text("No DNA profiles — run: dna init \"Character Name\"", style="dim")
    table = Table(title="🧬 Characters", box=box.SIMPLE, expand=True)
    table.add_column("Name", style="cyan")
    table.add_column("Slug", style="dim")
    table.add_column("Lock")
    for c in rows:
        status = c.get("status", "pending")
        color = LOCK_COLORS.get(status, "white")
        table.add_row(
            c["name"],
            c["slug"],
            Text(status, style=color),
        )
    total = snapshot["production"]["characters"]
    if total > len(rows):
        table.caption = f"Showing {len(rows)} of {total}"
    return table


def _nsfw_table(snapshot: dict[str, Any]) -> Table | None:
    rows = snapshot["nsfw_batches"]
    if not rows:
        return None
    table = Table(title="🔞 NSFW Batches", box=box.SIMPLE, expand=True)
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Status")
    table.add_column("Shots", justify="right")
    for b in rows:
        shots = b.get("shots_scheduled", b.get("shots_total", "—"))
        table.add_row(
            b.get("batch_id", "?")[:20],
            (b.get("title") or "")[:28],
            b.get("status", "—"),
            str(shots),
        )
    return table


def _quick_actions_panel() -> Panel:
    actions = (
        "[bold]Quick commands[/bold]\n"
        "  dashboard          — refresh this view\n"
        "  quota dashboard    — quota detail\n"
        "  sequence list      — all sequences\n"
        "  dna list           — character DNA\n"
        "  quota estimate -d 60 — session cost\n"
        "  validate           — workspace health"
    )
    return Panel(actions, border_style="dim", box=box.SIMPLE)


def dashboard_renderables(snapshot: dict[str, Any], *, compact: bool = False) -> Group:
    """Build Rich renderables for the studio dashboard."""
    parts: list[RenderableType] = [_header_panel(snapshot)]

    if not snapshot["studio"]["models_compatible"]:
        issues = snapshot["studio"].get("model_issues", [])
        parts.append(Panel("\n".join(f"• {i}" for i in issues), title="Model Issues", border_style="red"))

    parts.append(Columns([_studio_health_table(snapshot), _quota_table(snapshot)], equal=True, expand=True))
    parts.append(_production_summary(snapshot))

    if not compact:
        parts.append(_sequences_table(snapshot))
        parts.append(_characters_table(snapshot))
        nsfw = _nsfw_table(snapshot)
        if nsfw:
            parts.append(nsfw)
        if snapshot["quota"].get("recent_history"):
            hist = Table(title="📜 Recent Spend", box=box.SIMPLE, show_header=False)
            hist.add_column("When", style="dim")
            hist.add_column("Credits", justify="right")
            hist.add_column("Note")
            for entry in snapshot["quota"]["recent_history"][-5:]:
                hist.add_row(
                    str(entry.get("at", ""))[:19],
                    str(entry.get("credits", "")),
                    str(entry.get("note", ""))[:40],
                )
            parts.append(hist)

    parts.append(_quick_actions_panel())
    return Group(*parts)


def render_studio_dashboard(snapshot: dict[str, Any], *, compact: bool = False) -> None:
    """Print the studio dashboard to the shared Rich console."""
    console.print(dashboard_renderables(snapshot, compact=compact))


def render_dashboard_json(snapshot: dict[str, Any]) -> None:
    import json

    console.print(json.dumps(snapshot, indent=2))