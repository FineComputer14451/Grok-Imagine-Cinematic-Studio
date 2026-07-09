"""Release pin validation: pin may trail HEAD by catalog-only commits."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from plugin_catalog import (  # noqa: E402
    ALLOWED_POST_PIN_PATHS,
    validate_release_pin,
)


def _marketplace(sha: str) -> dict:
    return {
        "plugins": [
            {
                "name": "grok-imagine-cinematic-studio",
                "source": {
                    "source": "url",
                    "url": "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio.git",
                    "sha": sha,
                },
            }
        ]
    }


HEAD = "a" * 40
PIN = "b" * 40
OTHER = "c" * 40


def test_release_pin_equal_head_ok() -> None:
    with mock.patch("plugin_catalog.git_head_sha", return_value=HEAD), mock.patch(
        "plugin_catalog.git_commit_exists", return_value=True
    ):
        assert validate_release_pin(_marketplace(HEAD)) == []


def test_release_pin_ancestor_catalog_only_ok() -> None:
    with (
        mock.patch("plugin_catalog.git_head_sha", return_value=HEAD),
        mock.patch("plugin_catalog.git_commit_exists", return_value=True),
        mock.patch("plugin_catalog.git_is_ancestor", return_value=True),
        mock.patch(
            "plugin_catalog.git_diff_names",
            return_value=sorted(ALLOWED_POST_PIN_PATHS),
        ),
    ):
        assert validate_release_pin(_marketplace(PIN)) == []


def test_release_pin_content_after_pin_fails() -> None:
    with (
        mock.patch("plugin_catalog.git_head_sha", return_value=HEAD),
        mock.patch("plugin_catalog.git_commit_exists", return_value=True),
        mock.patch("plugin_catalog.git_is_ancestor", return_value=True),
        mock.patch(
            "plugin_catalog.git_diff_names",
            return_value=[
                ".grok-plugin/marketplace.json",
                "tools/plugin_catalog.py",
            ],
        ),
    ):
        errs = validate_release_pin(_marketplace(PIN))
        assert errs
        assert any("content changed after marketplace pin" in e for e in errs)
        assert any("plugin_catalog.py" in e for e in errs)


def test_release_pin_not_ancestor_fails() -> None:
    with (
        mock.patch("plugin_catalog.git_head_sha", return_value=HEAD),
        mock.patch("plugin_catalog.git_commit_exists", return_value=True),
        mock.patch("plugin_catalog.git_is_ancestor", return_value=False),
    ):
        errs = validate_release_pin(_marketplace(OTHER))
        assert errs
        assert any("not an ancestor" in e for e in errs)


def test_release_pin_unknown_commit_fails() -> None:
    with (
        mock.patch("plugin_catalog.git_head_sha", return_value=HEAD),
        mock.patch("plugin_catalog.git_commit_exists", return_value=False),
    ):
        errs = validate_release_pin(_marketplace(PIN))
        assert errs
        assert any("not a commit" in e for e in errs)


def test_release_pin_missing_sha_fails() -> None:
    with mock.patch("plugin_catalog.git_head_sha", return_value=HEAD):
        errs = validate_release_pin({"plugins": []})
        assert errs
        assert any("missing pinned sha" in e for e in errs)


def test_live_repo_release_pin_passes() -> None:
    """Current main should pass after pin-only commit on top of content pin."""
    import json

    from studio_paths import PLUGIN_MARKETPLACE_PATH

    marketplace = json.loads(PLUGIN_MARKETPLACE_PATH.read_text(encoding="utf-8"))
    errs = validate_release_pin(marketplace)
    assert errs == [], errs
