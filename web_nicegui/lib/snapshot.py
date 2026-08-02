"""Load studio dashboard snapshot via studio_core (UI-agnostic)."""

from __future__ import annotations

from typing import Any

from studio_core.pathutil import ensure_import_paths
from studio_core.services.dashboard import build_studio_dashboard

# TUI-parity density modes
DASHBOARD_VIEW_MODES: tuple[str, ...] = ("compact", "ops", "full")

DASHBOARD_MODE_SECTIONS: dict[str, frozenset[str]] = {
    "compact": frozenset({"health_actions", "readiness"}),
    "ops": frozenset(
        {
            "health_actions",
            "readiness",
            "convergence",
            "delivery",
            "studio_quota",
            "stack",
            "chain_qa",
        }
    ),
    "full": frozenset(
        {
            "health_actions",
            "readiness",
            "convergence",
            "briefs",
            "delivery",
            "studio_quota",
            "stack",
            "sequences",
            "chain_qa",
            "characters",
            "jobs",
            "batches",
            "spend",
            "json",
        }
    ),
}


def normalize_dashboard_mode(mode: str | None) -> str:
    m = (mode or "ops").strip().lower()
    return m if m in DASHBOARD_VIEW_MODES else "ops"


def section_visible(mode: str, section: str) -> bool:
    m = normalize_dashboard_mode(mode)
    allowed = DASHBOARD_MODE_SECTIONS.get(m, DASHBOARD_MODE_SECTIONS["ops"])
    return section in allowed


def attach_quota_alignment(snap: dict[str, Any]) -> dict[str, Any]:
    if "quota_alignment" in snap:
        return snap
    ensure_import_paths()
    try:
        from quota_sync import ledger_recon_alignment

        snap["quota_alignment"] = ledger_recon_alignment()
    except Exception:
        pass
    return snap


def load_snapshot() -> dict[str, Any]:
    """Build + enrich dashboard snapshot (same contract as CLI/TUI/Streamlit)."""
    ensure_import_paths()
    snap = build_studio_dashboard()
    return attach_quota_alignment(snap)


def severity(snap: dict[str, Any]) -> str:
    ensure_import_paths()
    try:
        from cli.tui.widgets import strip_severity

        return strip_severity(snap)
    except Exception:
        return "ok"


def severity_label(sev: str) -> str:
    return {"ok": "OK", "warn": "WARN", "critical": "CRITICAL"}.get(sev, (sev or "OK").upper())


def studio_version(snap: dict[str, Any] | None = None) -> str:
    if snap and snap.get("studio_version"):
        return str(snap["studio_version"])
    try:
        from studio_core.pathutil import STUDIO_ROOT

        vf = STUDIO_ROOT / "VERSION"
        if vf.is_file():
            return vf.read_text(encoding="utf-8").strip() or "3.8.9"
    except Exception:
        pass
    return "3.8.9"
