"""PR1: studio_core dashboard service is UI-agnostic and shims cleanly."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from studio_core.services.dashboard import build_studio_dashboard as core_build  # noqa: E402
from cli.dashboard import build_studio_dashboard as cli_build  # noqa: E402


REQUIRED_TOP_KEYS = {
    "generated_at",
    "studio_version",
    "project",
    "studio",
    "quota",
    "production",
    "readiness",
    "imagine_jobs",
    "sequences",
    "characters",
    "nsfw_batches",
    "sfw_batches",
    "recent_jobs",
    "chain_qa",
    "production_report",
    "artifacts",
}


def test_core_build_studio_dashboard_shape() -> None:
    snap = core_build()
    missing = REQUIRED_TOP_KEYS - set(snap)
    assert not missing, f"missing keys: {missing}"
    assert snap["studio_version"]
    assert snap["studio"]["core_agents"] >= 23
    recon = snap["quota"].get("reconciliation") or {}
    assert "cascade_source" in recon
    assert "entry_count" in recon


def test_cli_shim_is_same_function() -> None:
    """cli.dashboard re-exports the core builder (identity, not just shape)."""
    assert cli_build is core_build


def test_core_module_has_no_rich_dependency_at_import() -> None:
    """dashboard service module source must not import rich/streamlit/textual."""
    src = (ROOT / "studio_core" / "services" / "dashboard.py").read_text(encoding="utf-8")
    for ban in ("import rich", "from rich", "import streamlit", "import textual", "from textual"):
        assert ban not in src, f"forbidden import pattern: {ban}"


if __name__ == "__main__":
    test_core_build_studio_dashboard_shape()
    test_cli_shim_is_same_function()
    test_core_module_has_no_rich_dependency_at_import()
    print("studio_core dashboard tests passed")
