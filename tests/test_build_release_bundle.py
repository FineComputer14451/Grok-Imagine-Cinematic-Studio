"""Release zip includes studio_core + TUI (Method A CLI payload)."""

from __future__ import annotations

import os
import stat
import subprocess
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
BUILDER = ROOT / "scripts" / "build_release_bundle.sh"


def test_release_bundle_includes_studio_core_and_tui(tmp_path: Path) -> None:
    if not (ROOT / ".grok" / "skills" / "studio-director" / "SKILL.md").is_file():
        pytest.skip("full skill tree not present")
    out = tmp_path / "bundle.zip"
    env = {**os.environ, "CINEMATIC_SKIP_GROK_CLI": "1"}
    result = subprocess.run(
        ["bash", str(BUILDER), str(out)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert out.is_file()
    assert out.stat().st_mode & stat.S_IWUSR
    with zipfile.ZipFile(out) as zf:
        names = set(zf.namelist())
    assert "studio_core/services/dashboard.py" in names
    assert "tools/cli/tui/__init__.py" in names
    assert "tools/cinematic_studio_cli.py" in names
    assert ".grok/skills/studio-director/SKILL.md" in names
