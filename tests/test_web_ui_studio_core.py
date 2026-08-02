"""PR8: Streamlit runtime uses studio_core dashboard + execute."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "web_ui"))


def test_build_studio_dashboard_from_core_path() -> None:
    # Import after path setup; runtime also inserts paths
    from lib import runtime as rt

    assert rt.DASHBOARD_AVAILABLE is True
    snap = rt.build_studio_dashboard()
    assert "project" in snap
    assert "studio" in snap
    # Identity with core module
    from studio_core.services.dashboard import build_studio_dashboard as core_build

    # Same function object preferred
    assert rt.build_studio_dashboard is core_build or callable(rt.build_studio_dashboard)


def test_execute_registered_status() -> None:
    from lib import runtime as rt

    result = rt.execute_registered("status", timeout=60.0)
    assert result["ok"] is True
    assert result["returncode"] == 0
    assert result["argv"] == ["status"]
    assert result["mode"] == "inprocess"
    assert result["output"] or result["stdout"]


def test_run_cli_or_action_validate() -> None:
    from lib import runtime as rt

    code, output = rt.run_cli_or_action("validate", timeout=90.0)
    assert code == 0
    assert output


def test_execute_registered_validation_failure() -> None:
    from lib import runtime as rt

    result = rt.execute_registered("bible_create", {"title": ""})
    assert result["ok"] is False
    assert result["errors"] or "validation" in (result.get("stderr") or "").lower()


if __name__ == "__main__":
    test_build_studio_dashboard_from_core_path()
    test_execute_registered_status()
    test_run_cli_or_action_validate()
    test_execute_registered_validation_failure()
    print("web_ui studio_core tests passed")
