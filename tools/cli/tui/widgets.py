"""Pure formatters: dashboard snapshot → text for Textual widgets.

No Textual imports — unit-testable without a TTY.
"""

from __future__ import annotations

from typing import Any


def format_error_panel(message: str) -> str:
    """Markdown-friendly error (legacy / Markdown widgets)."""
    return f"## Error\n\n{message}\n\nPress **r** to retry · **q** to quit."


def format_home_error(message: str) -> str:
    """Plain-text error for Static home panels."""
    return (
        f"Error\n\n{message}\n\n"
        "Press r to retry · q to quit."
    )


def format_form_errors(errors: list[str]) -> str:
    """Plain text for Static widgets (not Markdown)."""
    if not errors:
        return ""
    lines = ["Validation errors:", ""]
    for e in errors:
        lines.append(f"• {e}")
    return "\n".join(lines)


def format_home_hints() -> str:
    return (
        "Keys: r refresh · s quota sync · d doctor · v validate · "
        "m models · k stack · l launcher · c cockpit · ? help · q quit"
    )


def _chain_qa_totals(snapshot: dict[str, Any]) -> tuple[int, int]:
    rows = snapshot.get("chain_qa") or []
    go = 0
    no_go = 0
    for r in rows:
        if not isinstance(r, dict):
            continue
        go += int(r.get("go_count") or 0)
        no_go += int(r.get("no_go_count") or 0)
    return go, no_go


def _chain_qa_rollup(snapshot: dict[str, Any]) -> str:
    rows = snapshot.get("chain_qa") or []
    if not rows:
        return "QA —"
    go, no_go = _chain_qa_totals(snapshot)
    return f"QA {go} go · {no_go} no-go"


def _risk_label(level: str) -> str:
    return (level or "unknown").strip().lower() or "unknown"


def _alignment_status(snapshot: dict[str, Any]) -> tuple[str | None, str]:
    if isinstance(snapshot.get("quota_alignment"), dict):
        status = snapshot["quota_alignment"].get("status")
        hint = str(snapshot["quota_alignment"].get("hint") or "")
        return (str(status) if status is not None else None, hint)
    try:
        from quota_sync import ledger_recon_alignment

        align = ledger_recon_alignment()
        return (str(align.get("status") or "") or None, str(align.get("hint") or ""))
    except Exception:
        return (None, "")


def strip_severity(snapshot: dict[str, Any]) -> str:
    """CSS severity for status strip: ok | warn | critical."""
    studio = snapshot.get("studio") or {}
    quota = snapshot.get("quota") or {}
    risk = _risk_label(str(quota.get("risk_level") or "unknown"))
    _, no_go = _chain_qa_totals(snapshot)
    align, _ = _alignment_status(snapshot)

    if not studio.get("models_compatible") or risk == "critical":
        return "critical"
    if no_go > 0 or risk == "high":
        return "critical"
    if risk == "medium" or (align and align not in ("aligned", "idle")):
        return "warn"
    production = snapshot.get("production") or {}
    locked = int(production.get("identity_locked") or 0)
    chars = int(production.get("characters") or 0)
    if chars and locked < chars:
        return "warn"
    if not (snapshot.get("project") or {}).get("has_bible"):
        return "warn"
    return "ok"


def collect_home_alerts(snapshot: dict[str, Any]) -> list[str]:
    """Actionable attention items derived only from the dashboard snapshot."""
    alerts: list[str] = []
    project = snapshot.get("project") or {}
    studio = snapshot.get("studio") or {}
    quota = snapshot.get("quota") or {}
    production = snapshot.get("production") or {}

    if not project.get("has_bible"):
        alerts.append("Production Bible not started — open Cockpit → Create Bible")
    if not studio.get("models_compatible"):
        issues = studio.get("model_issues") or []
        detail = f": {issues[0]}" if issues else ""
        alerts.append(f"Model stack ISSUES{detail} — run Models Verify (launcher)")
    risk = _risk_label(str(quota.get("risk_level") or "unknown"))
    if risk in ("high", "critical"):
        alerts.append(f"Quota risk is {risk} — review spend or raise budget")
    elif risk == "medium":
        alerts.append("Quota risk is medium — watch session burn")

    align, align_hint = _alignment_status(snapshot)
    if align and align not in ("aligned", "idle"):
        hint = f" ({align_hint})" if align_hint else ""
        alerts.append(f"Ledger alignment: {align}{hint} — press s for quota sync")

    locked = int(production.get("identity_locked") or 0)
    chars = int(production.get("characters") or 0)
    if chars and locked < chars:
        alerts.append(f"Identity lock incomplete: {locked}/{chars} locked — Cockpit → DNA lock")

    go, no_go = _chain_qa_totals(snapshot)
    if no_go > 0:
        alerts.append(f"Chain QA no-go: {no_go} clip(s) across sequences (go {go})")
        for r in (snapshot.get("chain_qa") or [])[:4]:
            if not isinstance(r, dict):
                continue
            if int(r.get("no_go_count") or 0) <= 0:
                continue
            name = r.get("sequence_name") or r.get("slug") or "sequence"
            alerts.append(
                f"  ↳ {name}: {r.get('no_go_count')} no-go / {r.get('go_count', 0)} go"
            )

    # De-dupe while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for a in alerts:
        if a not in seen:
            seen.add(a)
            out.append(a)
    return out[:8]


def format_attention_panel(snapshot: dict[str, Any]) -> str:
    """Always-visible attention board (all-clear when nothing is wrong)."""
    alerts = collect_home_alerts(snapshot)
    lines = ["ATTENTION"]
    if not alerts:
        lines.append("  All clear — no blocking ops signals")
        return "\n".join(lines)
    for i, a in enumerate(alerts, 1):
        lines.append(f"  {i}. {a}")
    return "\n".join(lines)


def format_status_strip(snapshot: dict[str, Any]) -> str:
    """One-line ops rollup: project, bible, models, risk, DNA locks, QA."""
    project = snapshot.get("project") or {}
    studio = snapshot.get("studio") or {}
    quota = snapshot.get("quota") or {}
    production = snapshot.get("production") or {}

    title = project.get("title") or "Untitled"
    bible = "bible:loaded" if project.get("has_bible") else "bible:none"
    models = "models:OK" if studio.get("models_compatible") else "models:ISSUES"
    risk = f"risk:{_risk_label(str(quota.get('risk_level') or 'unknown'))}"

    locked = production.get("identity_locked", 0)
    chars = production.get("characters", 0)
    dna = f"DNA {locked}/{chars} locked"
    sev = strip_severity(snapshot).upper()

    version = snapshot.get("studio_version", "?")
    when = snapshot.get("generated_at") or ""
    header = f"Cinematic Studio v{version}  [{sev}]"
    if when:
        header = f"{header}  ·  {when}"

    strip = "  ·  ".join(
        [
            title,
            bible,
            models,
            risk,
            dna,
            _chain_qa_rollup(snapshot),
        ]
    )
    return f"{header}\n{strip}"


def format_quota_panel(snapshot: dict[str, Any]) -> str:
    quota = snapshot.get("quota") or {}
    remaining = quota.get("budget_remaining")
    remaining_s = f"{remaining} credits" if remaining is not None else "—"
    tier = quota.get("tier_label") or quota.get("tier") or "—"
    risk = _risk_label(str(quota.get("risk_level") or "unknown"))

    lines = [
        "QUOTA",
        f"  Tier        {tier}",
        f"  Spent       {quota.get('session_spent', 0)} credits",
        f"  Remaining   {remaining_s}",
        f"  Risk        {risk}",
    ]
    recon = quota.get("reconciliation") or {}
    cascade = recon.get("cascade_source")
    if cascade and cascade != "none":
        lines.append(
            f"  Cascade     {cascade} · burn {recon.get('burn_rate_multiplier', 1.0)}x"
        )
        lines.append(
            f"  Recon       est {recon.get('estimated_total', 0)} / "
            f"act {recon.get('actual_total', 0)} "
            f"({recon.get('entry_count', 0)} entries)"
        )

    align_status, align_hint = _alignment_status(snapshot)
    if align_status:
        lines.append(f"  Alignment   {align_status}")
        if align_status not in ("aligned", "idle") and align_hint:
            lines.append(f"  Hint        {align_hint}")

    return "\n".join(lines)


def format_studio_panel(snapshot: dict[str, Any]) -> str:
    studio = snapshot.get("studio") or {}
    stack = studio.get("model_stack") or {}
    models = "compatible" if studio.get("models_compatible") else "ISSUES"
    production = snapshot.get("production") or {}

    lines = [
        "STUDIO",
        f"  Agents      {studio.get('core_agents', '?')} core · "
        f"{studio.get('total_agents', '?')} total",
        f"  Role cards  {studio.get('role_cards', '?')}/"
        f"{studio.get('role_cards_expected', '?')}",
        f"  Skills      {studio.get('skills', '?')}",
        f"  Models      {models}",
        f"  Chat        {stack.get('xai_chat', '—')}",
        f"  Video       {stack.get('imagine_video', '—')}",
        f"  Sequences   {production.get('sequences', 0)}  ·  "
        f"DNA {production.get('characters', 0)}  ·  "
        f"Jobs {production.get('imagine_jobs', 0)}",
        f"  Batches     SFW {production.get('sfw_batches', 0)} / "
        f"NSFW {production.get('nsfw_batches', 0)}",
    ]
    issues = studio.get("model_issues") or []
    if issues and not studio.get("models_compatible"):
        for issue in issues[:3]:
            lines.append(f"  ! {issue}")
    return "\n".join(lines)


def format_sequences_panel(snapshot: dict[str, Any]) -> str:
    seqs = snapshot.get("sequences") or []
    lines = ["SEQUENCES"]
    if not seqs:
        lines.append("  No sequences yet")
        return "\n".join(lines)
    for s in seqs[:8]:
        if not isinstance(s, dict):
            continue
        name = s.get("name") or s.get("slug") or "?"
        clips = s.get("clips", 0)
        health = s.get("health") or "—"
        dur = s.get("target_duration")
        dur_s = f"{dur}s" if dur is not None else "—"
        lines.append(f"  {name}  ·  {clips} clips  ·  health {health}  ·  target {dur_s}")
    return "\n".join(lines)


def format_chain_qa_panel(snapshot: dict[str, Any]) -> str:
    rows = snapshot.get("chain_qa") or []
    lines = ["CHAIN QA"]
    if not rows:
        lines.append("  No sequence QA data")
        return "\n".join(lines)
    for r in rows[:8]:
        if not isinstance(r, dict):
            continue
        name = r.get("sequence_name") or r.get("slug") or "?"
        go = r.get("go_count", 0)
        no_go = r.get("no_go_count", 0)
        status = r.get("chain_qa_status") or "—"
        clips = r.get("clip_count", "—")
        lines.append(
            f"  {name}  ·  go {go} / no-go {no_go}  ·  {status}  ·  clips {clips}"
        )
    return "\n".join(lines)


def format_characters_panel(snapshot: dict[str, Any]) -> str:
    chars = snapshot.get("characters") or []
    lines = ["CHARACTERS"]
    if not chars:
        lines.append("  No DNA profiles yet")
        return "\n".join(lines)
    for c in chars[:8]:
        if not isinstance(c, dict):
            continue
        name = c.get("name") or "?"
        slug = c.get("slug") or ""
        status = c.get("status") or "pending"
        lines.append(f"  {name}  ({slug})  ·  {status}")
    return "\n".join(lines)


def format_jobs_panel(snapshot: dict[str, Any]) -> str | None:
    """Return jobs panel text, or None when there are no recent jobs (omit panel)."""
    jobs = snapshot.get("recent_jobs") or []
    if not jobs:
        return None
    lines = ["RECENT JOBS"]
    for j in jobs[:6]:
        if not isinstance(j, dict):
            continue
        jid = j.get("job_id") or "?"
        jtype = j.get("job_type") or "—"
        status = j.get("status") or "—"
        model = j.get("model") or ""
        model_s = f"  ·  {model}" if model else ""
        lines.append(f"  {jid}  ·  {jtype}  ·  {status}{model_s}")
    return "\n".join(lines)


def format_home_markdown(snapshot: dict[str, Any]) -> str:
    """Compat: dense multi-section plain text (also used if a single body is needed)."""
    parts = [
        format_status_strip(snapshot),
        "",
        format_attention_panel(snapshot),
        "",
        format_quota_panel(snapshot),
        "",
        format_studio_panel(snapshot),
        "",
        format_sequences_panel(snapshot),
        "",
        format_chain_qa_panel(snapshot),
        "",
        format_characters_panel(snapshot),
    ]
    jobs = format_jobs_panel(snapshot)
    if jobs:
        parts.extend(["", jobs])
    parts.extend(["", format_home_hints()])
    return "\n".join(parts)
