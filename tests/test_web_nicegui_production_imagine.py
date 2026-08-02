"""PR6: NiceGUI Production + Imagine pages via execute_action."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from web_nicegui.lib.actions_ui import run_registered  # noqa: E402
from web_nicegui.pages import imagine, production  # noqa: E402


def test_page_builders_exist() -> None:
    assert callable(production.build_production_page)
    assert callable(imagine.build_imagine_page)


def test_run_status_and_imagine_list() -> None:
    status = run_registered("status", timeout=60.0)
    assert status.ok is True
    assert status.argv == ["status"]

    jobs = run_registered("imagine_list", timeout=60.0)
    assert jobs.ok is True
    assert jobs.argv == ["imagine", "list"]


def test_models_verify_and_validate() -> None:
    models = run_registered("models_verify", timeout=90.0)
    assert models.ok is True
    assert models.argv == ["models", "verify"]

    val = run_registered("validate", timeout=90.0)
    assert val.ok is True
    assert val.argv == ["validate"]


def test_bible_create_validation_failure() -> None:
    result = run_registered("bible_create", {"title": ""}, timeout=30.0)
    assert result.ok is False


def test_nav_includes_production_and_imagine() -> None:
    from web_nicegui.lib.layout import NAV

    paths = {p for p, _ in NAV}
    assert "/production" in paths
    assert "/imagine" in paths
    assert "/dna" in paths


def test_create_app_registers_new_routes() -> None:
    try:
        import nicegui  # noqa: F401
    except ImportError:
        return
    from web_nicegui.app import create_app

    assert create_app() is not None


def test_run_registered_error_path_no_crash() -> None:
    with patch("web_nicegui.lib.actions_ui.execute_action", side_effect=RuntimeError("x")):
        r = run_registered("status")
    assert r.ok is False
    assert "x" in r.stderr


if __name__ == "__main__":
    test_page_builders_exist()
    test_run_status_and_imagine_list()
    test_models_verify_and_validate()
    test_bible_create_validation_failure()
    test_nav_includes_production_and_imagine()
    test_create_app_registers_new_routes()
    test_run_registered_error_path_no_crash()
    print("PR6 tests passed")
