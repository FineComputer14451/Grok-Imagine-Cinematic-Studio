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


# Home density modes (v3.8.8+ UX polish)
HOME_VIEW_MODES: tuple[str, ...] = ("compact", "ops", "full")

# Panels visible per mode (ids without #). strip/attention/hints always on.
HOME_MODE_PANELS: dict[str, frozenset[str]] = {
    "compact": frozenset(
        {
            "panel-readiness",
        }
    ),
    "ops": frozenset(
        {
            "panel-readiness",
            "panel-convergence",
            "panel-delivery",
            "panel-quota",
            "panel-studio",
            "panel-chain-qa",
        }
    ),
    "full": frozenset(
        {
            "panel-readiness",
            "panel-convergence",
            "panel-briefs",
            "panel-delivery",
            "panel-quota",
            "panel-studio",
            "panel-sequences",
            "panel-chain-qa",
            "panel-characters",
            "panel-jobs",
        }
    ),
}


def format_home_hints(
    *,
    mode: str = "ops",
    paused: bool = False,
    refreshed_at: str = "",
) -> str:
    mode = mode if mode in HOME_VIEW_MODES else "ops"
    pause = "paused" if paused else "live"
    when = f" · updated {refreshed_at}" if refreshed_at else ""
    return (
        f"View [{mode}] · refresh {pause}{when} · "
        "1/2/3 views · p pause · / palette · y save brief · "
        "r refresh · s quota · d doctor · v validate · "
        "m models · k stack · l launcher · c cockpit · ? help · q quit"
    )


def next_home_mode(current: str) -> str:
    modes = HOME_VIEW_MODES
    try:
        i = modes.index(current)
    except ValueError:
        return "ops"
    return modes[(i + 1) % len(modes)]


def format_kpi_bar(snapshot: dict[str, Any]) -> str:
    """One-line KPI strip always visible under the status strip."""
    production = snapshot.get("production") or {}
    quota = snapshot.get("quota") or {}
    readiness = snapshot.get("readiness") or {}
    conv = snapshot.get("convergence") or {}
    delivery = snapshot.get("delivery") or {}
    go, no_go = _chain_qa_totals(snapshot)
    risk = _risk_label(str(quota.get("risk_level") or "unknown"))
    locked = production.get("identity_locked", 0)
    chars = production.get("characters", 0)
    overall = str(readiness.get("overall") or "—").upper()
    conv_lbl = conv.get("label") or "—"
    del_lbl = delivery.get("label") or "—"
    return (
        f"KPI  sequences {production.get('sequences', 0)}  ·  "
        f"DNA {locked}/{chars}  ·  risk {risk}  ·  "
        f"QA {go}g/{no_go}n  ·  gate {overall}  ·  "
        f"converge {conv_lbl}  ·  deliver {del_lbl}"
    )


def format_orient_brief(snapshot: dict[str, Any]) -> str:
    """Exportable orient summary (status + attention + KPIs + readiness next)."""
    parts = [
        format_status_strip(snapshot),
        "",
        format_kpi_bar(snapshot),
        "",
        format_attention_panel(snapshot),
        "",
        format_readiness_panel(snapshot),
    ]
    return "\n".join(parts)


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
    readiness = snapshot.get("readiness") or {}

    if not studio.get("models_compatible") or risk == "critical":
        return "critical"
    if no_go > 0 or risk == "high" or readiness.get("overall") == "blocked":
        return "critical"
    if risk == "medium" or (align and align not in ("aligned", "idle")):
        return "warn"
    if readiness.get("overall") == "partial":
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
    readiness = snapshot.get("readiness") or {}

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
        alerts.append(
            f"Identity lock incomplete: {locked}/{chars} locked — "
            "Cockpit DNA lock, then dna handoff / Web DNA 🔒"
        )

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
                f"  ↳ {name}: fix clip → re-QA → sequence handoff (do not extend yet)"
            )

    # Phase 2 readiness next_actions (deduped into attention)
    for action in readiness.get("next_actions") or []:
        alerts.append(str(action))

    # De-dupe while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for a in alerts:
        if a not in seen:
            seen.add(a)
            out.append(a)
    return out[:10]


def format_readiness_panel(snapshot: dict[str, Any]) -> str:
    """Produce/gate readiness (identity · plate/motion · chain QA)."""
    r = snapshot.get("readiness") or {}
    if not r:
        return "READINESS\n  (not available — refresh snapshot)"
    ident = r.get("identity") or {}
    pm = r.get("plate_motion") or {}
    cq = r.get("chain_qa") or {}
    overall = str(r.get("overall") or "unknown").upper()
    lines = [
        f"READINESS  [{overall}]",
        f"  Identity    {ident.get('label', '—')}",
        f"  Chain QA    {cq.get('label', '—')}",
    ]
    if pm.get("available"):
        lines.append(
            f"  Plates      ok {pm.get('plate_ok', 0)} · pending {pm.get('plate_pending', 0)} "
            f"(scanned {pm.get('scanned_shots', 0)})"
        )
        lines.append(
            f"  Motion      ok {pm.get('motion_ok', 0)} · pending {pm.get('motion_pending', 0)} "
            f"of {pm.get('video_shots', 0)} video shots"
        )
    else:
        lines.append("  Plates/Motion  (no SFW batch scan)")
    next_actions = r.get("next_actions") or []
    if next_actions:
        lines.append("  Next:")
        for a in next_actions[:4]:
            lines.append(f"    → {a}")
    elif overall == "READY":
        lines.append("  Next: gate clear for careful video spend")
    return "\n".join(lines)


def format_produce_gate_next_steps(action_id: str, *, ok: bool) -> str:
    """Post-action coaching after DNA/sequence produce steps (Phase 2)."""
    if not ok:
        return ""
    tips = {
        "dna_lock": (
            "Next: dna handoff → validate with `handoff validate <path>` · "
            "then inject / plate lock before i2v"
        ),
        "dna_handoff": (
            "Next: `handoff validate` the packet · Identity Lock Specialist · "
            "lock remaining cast if multi-character"
        ),
        "dna_init": "Next: complete facial/core fields if empty · dna lock when ready",
        "sequence_add_clip": (
            "Next: chain QA on the clip · if Go, sequence handoff · if No-Go, fix then re-QA"
        ),
        "sequence_handoff": (
            "Next: `handoff validate` packet · do not extend while Chain QA shows no-go"
        ),
        "sequence_init": "Next: add clips · lock DNA for cast · run chain QA before extend",
        "bible_create": "Next: dna init/lock · sequence init · quota budget · models verify",
        "handoff_validate": "If OK: safe to proceed with extend/agent-handoff under strict flags as needed",
        "sequence_polish_dry": (
            "If readiness OK: real polish without --dry-run on CLI after QA Go + color grade"
        ),
        "sequence_deliver_dry": (
            "If polish media ready: sequence deliver without --dry-run · then social crops"
        ),
        "imagine_bridge": (
            "Paste packet into grok.com/imagine · keep VIDEO_PIPELINE_SPEC · no silent NSFW"
        ),
        "wave_a_briefs": (
            "Log briefs under artifacts · converge specialists → handoff validate → agent-handoff"
        ),
    }
    return tips.get(action_id, "")


def format_parallel_briefs_panel(snapshot: dict[str, Any]) -> str:
    """J8 Parallel Brief log viewer (read-only)."""
    pb = snapshot.get("parallel_briefs") or {}
    logs = pb.get("logs") or []
    lines = ["PARALLEL BRIEFS  (J8 · read-only)"]
    lines.append(f"  {pb.get('label', '—')}")
    if not logs:
        lines.append("  No brief logs on disk yet")
        lines.append("  Next: wave-a briefs <session> -o artifacts/briefs_<session>.json")
        return "\n".join(lines)
    for log in logs[:6]:
        if not isinstance(log, dict):
            continue
        sid = log.get("session_id") or "?"
        n = log.get("brief_count", 0)
        specs = ", ".join(log.get("specialists") or []) or "—"
        lines.append(f"  {sid}  ·  {n} brief(s)  ·  {specs}")
        lines.append(f"    {log.get('path', '')}")
    lines.append("  Next: converge → handoff validate → imagine agent-handoff")
    return "\n".join(lines)


def format_convergence_panel(snapshot: dict[str, Any]) -> str:
    """J8 convergence checklist into imagine_agent_mode_handoff."""
    conv = snapshot.get("convergence") or {}
    checklist = conv.get("checklist") or []
    lines = [f"CONVERGENCE  [{conv.get('label', '—')}]"]
    if conv.get("ready"):
        lines.append("  Status: READY to validate agent-mode handoff")
    elif checklist:
        lines.append("  Status: HOLD — clear failing gates first")
    else:
        lines.append("  Status: unknown")
    for item in checklist:
        if not isinstance(item, dict):
            continue
        ok = item.get("ok")
        mark = "✓" if ok is True else ("·" if ok is None else "✗")
        lines.append(f"  {mark} {item.get('label', item.get('id', '?'))}")
        if ok is False and item.get("hint"):
            lines.append(f"      → {item['hint']}")
        if ok is None and item.get("hint"):
            lines.append(f"      → {item['hint']}")
    return "\n".join(lines)


def format_delivery_panel(snapshot: dict[str, Any]) -> str:
    """J7 delivery readiness (polish / deliver soft gates)."""
    d = snapshot.get("delivery") or {}
    rows = d.get("sequences") or []
    lines = [f"DELIVERY  [{d.get('label', '—')}]"]
    if not rows:
        lines.append("  No sequences to assess")
        lines.append("  Next: sequence polish --dry-run · sequence deliver --dry-run")
        return "\n".join(lines)
    for r in rows[:6]:
        if not isinstance(r, dict):
            continue
        name = r.get("name") or r.get("slug") or "?"
        p = "ok" if r.get("polish_pass") else "hold"
        de = "ok" if r.get("deliver_pass") else "hold"
        lines.append(f"  {name}  ·  polish {p}  ·  deliver {de}")
        for b in (r.get("polish_blockers") or [])[:1]:
            lines.append(f"    ! polish: {b}")
        for b in (r.get("deliver_blockers") or [])[:1]:
            lines.append(f"    ! deliver: {b}")
    lines.append("  Safe TUI: sequence polish/deliver --dry-run only (no silent spend)")
    return "\n".join(lines)


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
        lines.append("  Next: generate clips → run chain QA before extend")
        return "\n".join(lines)
    any_no_go = False
    for r in rows[:8]:
        if not isinstance(r, dict):
            continue
        name = r.get("sequence_name") or r.get("slug") or "?"
        go = r.get("go_count", 0)
        no_go = r.get("no_go_count", 0)
        status = r.get("chain_qa_status") or "—"
        clips = r.get("clip_count", "—")
        flag = " ⚠" if int(no_go or 0) > 0 else ""
        if int(no_go or 0) > 0:
            any_no_go = True
        lines.append(
            f"  {name}  ·  go {go} / no-go {no_go}  ·  {status}  ·  clips {clips}{flag}"
        )
    if any_no_go:
        lines.append("  Next: fix No-Go clips → re-QA → only then sequence handoff/extend")
    else:
        lines.append("  Next: sequence handoff OK when Go · validate packet before stitch")
    readiness = snapshot.get("readiness") or {}
    for a in (readiness.get("next_actions") or [])[:2]:
        if "QA" in a or "no-go" in a.lower() or "No-Go" in a:
            lines.append(f"  → {a}")
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
        format_kpi_bar(snapshot),
        "",
        format_attention_panel(snapshot),
        "",
        format_readiness_panel(snapshot),
        "",
        format_convergence_panel(snapshot),
        "",
        format_parallel_briefs_panel(snapshot),
        "",
        format_delivery_panel(snapshot),
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
