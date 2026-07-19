"""Pure formatters: dashboard snapshot → text for Textual widgets."""

from __future__ import annotations

from typing import Any


def format_error_panel(message: str) -> str:
    return f"## Error\n\n{message}\n\nPress **r** to retry · **q** to quit."


def format_home_markdown(snapshot: dict[str, Any]) -> str:
    project = snapshot.get("project") or {}
    studio = snapshot.get("studio") or {}
    quota = snapshot.get("quota") or {}
    production = snapshot.get("production") or {}
    stack = studio.get("model_stack") or {}

    title = project.get("title") or "Untitled"
    genre = project.get("genre") or "—"
    models = "compatible" if studio.get("models_compatible") else "ISSUES"
    remaining = quota.get("budget_remaining")
    remaining_s = f"{remaining} credits" if remaining is not None else "—"

    lines = [
        f"# Grok Imagine Cinematic Studio v{snapshot.get('studio_version', '?')}",
        f"_{snapshot.get('generated_at', '')}_",
        "",
        f"**Project:** {title}  ",
        f"**Genre:** {genre}  ",
        f"**Bible:** {'loaded' if project.get('has_bible') else 'not started'}",
        "",
        "## Studio Health",
        f"- Agents: {studio.get('core_agents', '?')} core · {studio.get('total_agents', '?')} total",
        f"- Role cards: {studio.get('role_cards', '?')}/{studio.get('role_cards_expected', '?')}",
        f"- Skills: {studio.get('skills', '?')}",
        f"- Models: **{models}**",
        f"- Chat: `{stack.get('xai_chat', '—')}` · Video: `{stack.get('imagine_video', '—')}`",
        "",
        "## Quota",
        f"- Tier: {quota.get('tier_label', quota.get('tier', '—'))}",
        f"- Session spent: {quota.get('session_spent', 0)} credits",
        f"- Budget left: {remaining_s}",
        f"- Risk: **{quota.get('risk_level', 'unknown')}**",
        "",
        "## Production",
        f"- Sequences: {production.get('sequences', 0)}",
        f"- DNA profiles: {production.get('characters', 0)} "
        f"(locked: {production.get('identity_locked', 0)})",
        f"- Imagine jobs: {production.get('imagine_jobs', 0)}",
        f"- SFW / NSFW batches: {production.get('sfw_batches', 0)} / "
        f"{production.get('nsfw_batches', 0)}",
        "",
        "_Keys: **r** refresh · **l** launcher · **?** help · **q** quit_",
    ]

    # Compact sequence / character lines
    seqs = snapshot.get("sequences") or []
    if seqs:
        lines.append("")
        lines.append("## Sequences")
        for s in seqs[:6]:
            lines.append(
                f"- {s.get('name', '?')} · {s.get('clips', 0)} clips · "
                f"QA {s.get('chain_qa_status', 'pending')}"
            )

    chars = snapshot.get("characters") or []
    if chars:
        lines.append("")
        lines.append("## Characters")
        for c in chars[:6]:
            lines.append(f"- {c.get('name', '?')} (`{c.get('slug', '')}`) · {c.get('status', 'pending')}")

    return "\n".join(lines)
