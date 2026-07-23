"""Pure formatters: dashboard snapshot → text for Textual widgets."""

from __future__ import annotations

from typing import Any


def format_error_panel(message: str) -> str:
    return f"## Error\n\n{message}\n\nPress **r** to retry · **q** to quit."


def format_form_errors(errors: list[str]) -> str:
    """Plain text for Static widgets (not Markdown)."""
    if not errors:
        return ""
    lines = ["Validation errors:", ""]
    for e in errors:
        lines.append(f"• {e}")
    return "\n".join(lines)


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
    ]
    recon = quota.get("reconciliation") or {}
    cascade = recon.get("cascade_source")
    if cascade and cascade != "none":
        lines.append(f"- Cascade: `{cascade}` · burn {recon.get('burn_rate_multiplier', 1.0)}x")
        lines.append(
            f"- Recon: est {recon.get('estimated_total', 0)} / "
            f"act {recon.get('actual_total', 0)} "
            f"({recon.get('entry_count', 0)} entries)"
        )
    # Read-only ledger alignment (same helper as doctor / quota sync)
    align_status = None
    align_hint = ""
    if isinstance(snapshot.get("quota_alignment"), dict):
        align_status = snapshot["quota_alignment"].get("status")
        align_hint = str(snapshot["quota_alignment"].get("hint") or "")
    else:
        try:
            from quota_sync import ledger_recon_alignment

            align = ledger_recon_alignment()
            align_status = align.get("status")
            align_hint = str(align.get("hint") or "")
        except Exception:
            align_status = None
    if align_status:
        lines.append(f"- Ledger alignment: **{align_status}**")
        if align_status not in ("aligned", "idle") and align_hint:
            lines.append(f"- _{align_hint}_")
    lines.extend(
        [
            "",
            "## Production",
            f"- Sequences: {production.get('sequences', 0)}",
            f"- DNA profiles: {production.get('characters', 0)} "
            f"(locked: {production.get('identity_locked', 0)})",
            f"- Imagine jobs: {production.get('imagine_jobs', 0)}",
            f"- SFW / NSFW batches: {production.get('sfw_batches', 0)} / "
            f"{production.get('nsfw_batches', 0)}",
            "",
            "_Keys: **r** refresh · **s** quota sync · **l** launcher · **c** cockpit · **?** help · **q** quit_",
        ]
    )

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
