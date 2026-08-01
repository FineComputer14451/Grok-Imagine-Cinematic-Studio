from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..deps import StudioBackend, get_backend, require_api_key
from ..schemas.common import SnapshotOut
from ..services.snapshot import build_snapshot_response

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(require_api_key)],
)


@router.get(
    "/snapshot",
    response_model=SnapshotOut,
    summary="Full studio dashboard snapshot (TUI/Streamlit parity)",
)
def get_snapshot(
    backend: StudioBackend = Depends(get_backend),
    include_raw: bool = Query(
        default=True,
        description="Reserved — always returns full snapshot dict for now",
    ),
) -> SnapshotOut:
    """
    Returns the same conceptual payload as Streamlit Dashboard / TUI Home:

    - `snapshot`: `build_studio_dashboard()` (+ quota_alignment when available)
    - `severity`: `strip_severity(snap)` when TUI widgets import
    - `attention`: `collect_home_alerts(snap)` when available

    Mock mode returns a stable demo shape for React without the monorepo tools.
    """
    _ = include_raw
    return build_snapshot_response(backend)


@router.get(
    "/severity",
    summary="Severity + attention only (lightweight poll)",
)
def get_severity(backend: StudioBackend = Depends(get_backend)) -> dict:
    full = build_snapshot_response(backend)
    return {
        "source": full.source,
        "studio_version": full.studio_version,
        "severity": full.severity,
        "attention": full.attention,
        "project_title": (full.snapshot.get("project") or {}).get("title"),
    }
