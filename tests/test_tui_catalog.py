# tests/test_tui_catalog.py
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.tui.catalog import FORBIDDEN_ARGV_TOKENS, LAUNCHER_CATALOG  # noqa: E402


def test_catalog_non_empty() -> None:
    assert len(LAUNCHER_CATALOG) >= 8


def test_catalog_entries_have_stable_ids_and_argv() -> None:
    ids = [e.id for e in LAUNCHER_CATALOG]
    assert len(ids) == len(set(ids))
    for entry in LAUNCHER_CATALOG:
        assert entry.label.strip()
        assert entry.argv
        assert all(isinstance(a, str) and a for a in entry.argv)


def test_catalog_excludes_dangerous_tokens() -> None:
    for entry in LAUNCHER_CATALOG:
        for token in entry.argv:
            assert token not in FORBIDDEN_ARGV_TOKENS, f"{entry.id}: {token}"
        assert "--wizard" not in entry.argv


def test_catalog_includes_required_commands() -> None:
    argvs = {" ".join(e.argv) for e in LAUNCHER_CATALOG}
    for required in (
        "status",
        "dashboard --compact",
        "doctor --quick",
        "models list",
        "models verify",
        "quota dashboard",
        "dna list",
        "sequence list",
        "imagine list",
        "plugin list",
    ):
        assert required in argvs
