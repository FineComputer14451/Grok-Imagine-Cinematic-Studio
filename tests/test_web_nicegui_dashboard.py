"""PR4: NiceGUI dashboard snapshot wiring (no live server required)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from web_nicegui.lib.snapshot import (  # noqa: E402
    DASHBOARD_VIEW_MODES,
    load_snapshot,
    normalize_dashboard_mode,
    section_visible,
    severity,
    studio_version,
)


def test_normalize_mode() -> None:
    assert normalize_dashboard_mode("OPS") == "ops"
    assert normalize_dashboard_mode("nope") == "ops"
    assert set(DASHBOARD_VIEW_MODES) == {"compact", "ops", "full"}


def test_section_visibility() -> None:
    assert section_visible("compact", "readiness")
    assert not section_visible("compact", "jobs")
    assert section_visible("full", "jobs")
    assert section_visible("ops", "studio_quota")


def test_load_snapshot_shape() -> None:
    snap = load_snapshot()
    for key in (
        "generated_at",
        "studio_version",
        "project",
        "studio",
        "quota",
        "production",
        "readiness",
    ):
        assert key in snap
    assert studio_version(snap)
    assert severity(snap) in {"ok", "warn", "critical"}


def test_web_command_help() -> None:
    from cli_helpers import run_cli

    result = run_cli("web", "--help")
    assert result.returncode == 0, result.stderr
    assert "NiceGUI" in result.stdout or "nicegui" in result.stdout.lower() or "web" in result.stdout.lower()
    assert "--port" in result.stdout


def test_main_help_lists_web() -> None:
    from cli_helpers import run_cli

    result = run_cli("--help")
    assert result.returncode == 0
    assert "web" in result.stdout


def test_create_app_imports_when_nicegui_installed() -> None:
    try:
        import nicegui  # noqa: F401
    except ImportError:
        return  # optional dep
    from web_nicegui.app import create_app

    ui = create_app()
    assert ui is not None


if __name__ == "__main__":
    test_normalize_mode()
    test_section_visibility()
    test_load_snapshot_shape()
    test_web_command_help()
    test_main_help_lists_web()
    test_create_app_imports_when_nicegui_installed()
    print("web_nicegui tests passed")
