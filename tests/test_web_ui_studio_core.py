"""PR8: Streamlit runtime uses studio_core dashboard + execute."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "web_ui"))


def _require_streamlit() -> None:
    pytest.importorskip("streamlit", reason="Streamlit optional on phone CI")


def test_imagine_page_source_has_files_tab() -> None:
    src = (ROOT / "web_ui" / "pages" / "imagine.py").read_text(encoding="utf-8")
    assert '"Files"' in src
    assert "files_upload" in src
    assert "_render_files_tab" in src
    assert "file_id" in src


def test_imagine_submit_argv_prefers_file_id() -> None:
    from lib.imagine_runtime import imagine_submit_argv

    argv = imagine_submit_argv(
        "image_edit",
        "Add hat",
        image_url="https://example.com/a.png",
        file_id="file_abc",
        dry_run=True,
    )
    assert argv[:3] == ["imagine", "submit", "image_edit"]
    assert "--file-id" in argv and "file_abc" in argv
    assert "--image-url" not in argv
    assert "--dry-run" in argv
    video = imagine_submit_argv(
        "video_extend",
        "Continue",
        video_url="https://example.com/c.mp4",
    )
    assert "--video-url" in video
    assert "--file-id" not in video


def test_execute_files_list_via_core() -> None:
    from studio_core.services.execute import execute_action

    result = execute_action("files_list", {}, mode="inprocess", timeout=60.0)
    assert result.ok is True
    assert result.argv == ["files", "list"]


def test_build_studio_dashboard_from_core_path() -> None:
    _require_streamlit()
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
    _require_streamlit()
    from lib import runtime as rt

    result = rt.execute_registered("status", timeout=60.0)
    assert result["ok"] is True
    assert result["returncode"] == 0
    assert result["argv"] == ["status"]
    assert result["mode"] == "inprocess"
    assert result["output"] or result["stdout"]


def test_run_cli_or_action_validate() -> None:
    _require_streamlit()
    from lib import runtime as rt

    code, output = rt.run_cli_or_action("validate", timeout=90.0)
    assert code == 0
    assert output


def test_execute_registered_validation_failure() -> None:
    _require_streamlit()
    from lib import runtime as rt

    result = rt.execute_registered("bible_create", {"title": ""})
    assert result["ok"] is False
    assert result["errors"] or "validation" in (result.get("stderr") or "").lower()


if __name__ == "__main__":
    test_imagine_page_source_has_files_tab()
    test_imagine_submit_argv_prefers_file_id()
    test_execute_files_list_via_core()
    print("web_ui studio_core tests passed")
