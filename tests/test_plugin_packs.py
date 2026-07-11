from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from plugin_packs import (  # noqa: E402
    FULL_PLUGIN_NAME,
    PACK_IDS,
    PackValidationError,
    load_plugin_packs,
    resolve_pack_skill_paths,
    validate_plugin_packs,
)


def test_load_and_validate_default_config() -> None:
    cfg = load_plugin_packs()
    errors = validate_plugin_packs(cfg)
    assert errors == []
    assert cfg["full_plugin"]["name"] == FULL_PLUGIN_NAME
    assert set(cfg["packs"].keys()) == set(PACK_IDS)


def test_skill_membership_exclusive_and_covers_disk() -> None:
    cfg = load_plugin_packs()
    assert validate_plugin_packs(cfg) == []
    union: list[str] = []
    for pid in PACK_IDS:
        union.extend(cfg["packs"][pid]["skills"])
    assert len(union) == len(set(union))
    assert len(union) == 48


def test_commands_domain_mapped() -> None:
    cfg = load_plugin_packs()
    assert "nsfw" in cfg["packs"]["nsfw"]["commands"]
    assert "delivery" in cfg["packs"]["delivery-post"]["commands"]
    assert "cinematic" in cfg["packs"]["core"]["commands"]
    owned: dict[str, str] = {}
    for pid, pack in cfg["packs"].items():
        for cmd in pack.get("commands") or []:
            assert cmd not in owned, f"{cmd} in {owned[cmd]} and {pid}"
            owned[cmd] = pid


def test_resolve_paths_core() -> None:
    cfg = load_plugin_packs()
    paths = resolve_pack_skill_paths(cfg["packs"]["core"]["skills"])
    assert ".grok/skills/studio-director" in paths
    assert all(p.startswith(".grok/skills/") for p in paths)


def test_duplicate_skill_fails_validation() -> None:
    cfg = load_plugin_packs()
    cfg["packs"]["nsfw"]["skills"] = list(cfg["packs"]["nsfw"]["skills"]) + [
        cfg["packs"]["core"]["skills"][0]
    ]
    errs = validate_plugin_packs(cfg)
    assert errs
    assert any("duplicate" in e.lower() or "two packs" in e.lower() for e in errs)
