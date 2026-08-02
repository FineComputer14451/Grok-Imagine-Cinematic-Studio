"""PR5: NiceGUI DNA / Sequences / Quota pages + execute_action wiring."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from web_nicegui.lib.actions_ui import run_registered  # noqa: E402
from web_nicegui.pages import dna, quota, sequences  # noqa: E402


def test_run_registered_dna_list() -> None:
    result = run_registered("dna_list", timeout=60.0)
    assert result.action_id == "dna_list"
    assert result.mode == "inprocess"
    assert result.argv == ["dna", "list"]
    # empty workspace still succeeds
    assert result.returncode == 0
    assert result.ok is True


def test_run_registered_sequence_list() -> None:
    result = run_registered("sequence_list", timeout=60.0)
    assert result.ok is True
    assert result.argv == ["sequence", "list"]


def test_run_registered_quota_dashboard() -> None:
    result = run_registered("quota_dashboard", timeout=60.0)
    assert result.ok is True
    assert result.argv == ["quota", "dashboard"]


def test_page_builders_importable() -> None:
    assert callable(dna.build_dna_page)
    assert callable(sequences.build_sequences_page)
    assert callable(quota.build_quota_page)


def test_create_app_registers_routes() -> None:
    try:
        import nicegui  # noqa: F401
    except ImportError:
        return
    from web_nicegui.app import create_app

    ui = create_app()
    assert ui is not None


def test_dna_init_validation_failure() -> None:
    result = run_registered("dna_init", {"name": ""}, timeout=30.0)
    assert result.ok is False
    assert result.errors or "required" in (result.stderr or "").lower() or "validation" in (
        result.stderr or ""
    ).lower()


if __name__ == "__main__":
    test_run_registered_dna_list()
    test_run_registered_sequence_list()
    test_run_registered_quota_dashboard()
    test_page_builders_importable()
    test_create_app_registers_routes()
    test_dna_init_validation_failure()
    print("PR5 page tests passed")
