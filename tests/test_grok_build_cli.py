"""Grok Build CLI ensure helpers + cinematic-studio grok wiring."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools" / "cinematic_studio_cli.py"
sys.path.insert(0, str(ROOT / "tools"))

from grok_build_cli import (  # noqa: E402
    RECOMMENDED_GROK_BUILD_CLI_VERSION,
    _versioned_binary_key,
    find_grok_binary,
    probe_preferred,
)
from models import RECOMMENDED_GROK_BUILD_CLI_VERSION as MIN_VER  # noqa: E402


def test_min_version_aligned() -> None:
    assert RECOMMENDED_GROK_BUILD_CLI_VERSION == MIN_VER
    assert MIN_VER == "0.2.93"


def test_probe_preferred_shape() -> None:
    p = probe_preferred()
    assert "path" in p
    assert "version" in p
    assert "min_version" in p
    assert "meets_min" in p
    assert p["min_version"] == "0.2.93"


def test_find_grok_binary_type() -> None:
    found = find_grok_binary()
    assert found is None or isinstance(found, Path)


def test_versioned_binary_sort_is_semver() -> None:
    """Lexicographic sort would pick 0.2.9 over 0.2.112 — we must not."""
    names = [
        Path("grok-0.2.9"),
        Path("grok-0.2.112"),
        Path("grok-0.2.93"),
        Path("grok-0.2.100"),
    ]
    ordered = sorted(names, key=_versioned_binary_key)
    assert ordered[-1].name == "grok-0.2.112"
    assert ordered[0].name == "grok-0.2.9"


def test_cli_grok_status() -> None:
    r = subprocess.run(
        [sys.executable, str(CLI), "grok", "status"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr
    out = r.stdout + r.stderr
    assert "0.2.93" in out or "min" in out.lower() or "version" in out.lower()


def test_cli_grok_help() -> None:
    r = subprocess.run(
        [sys.executable, str(CLI), "grok", "--help"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0
    assert "ensure" in r.stdout
    assert "update" in r.stdout
    assert "install" in r.stdout
