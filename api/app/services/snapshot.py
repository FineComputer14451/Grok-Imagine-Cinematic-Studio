from __future__ import annotations

from typing import Any

from ..deps import StudioBackend, source_label, studio_version
from ..schemas.common import SnapshotOut
from .mock_data import mock_attention, mock_snapshot


def build_snapshot_response(backend: StudioBackend) -> SnapshotOut:
    if backend.live and backend.get("build_studio_dashboard"):
        snap: dict[str, Any] = dict(backend.get("build_studio_dashboard")())
        if "quota_alignment" not in snap and backend.get("ledger_recon_alignment"):
            try:
                snap["quota_alignment"] = backend.get("ledger_recon_alignment")()
            except Exception:
                pass
        sev = _severity(backend, snap)
        attention = _attention(backend, snap)
        return SnapshotOut(
            source="live",
            studio_version=studio_version(backend),
            severity=sev,  # type: ignore[arg-type]
            attention=attention,
            snapshot=snap,
        )

    snap = mock_snapshot()
    return SnapshotOut(
        source="mock",
        studio_version=studio_version(backend),
        severity="warn",
        attention=mock_attention(),
        snapshot=snap,
    )


def _severity(backend: StudioBackend, snap: dict[str, Any]) -> str:
    fn = backend.get("strip_severity")
    if callable(fn):
        try:
            return str(fn(snap) or "ok")
        except Exception:
            pass
    # Lightweight fallback mirroring TUI-ish signals
    alerts = _attention(backend, snap)
    if any("no-go" in a.lower() or "critical" in a.lower() for a in alerts):
        return "critical" if any("no-go" in a.lower() for a in alerts) else "warn"
    if alerts:
        return "warn"
    if not (snap.get("studio") or {}).get("models_compatible", True):
        return "warn"
    return "ok"


def _attention(backend: StudioBackend, snap: dict[str, Any]) -> list[str]:
    fn = backend.get("collect_home_alerts")
    if callable(fn):
        try:
            return list(fn(snap) or [])
        except Exception:
            pass
    return []
