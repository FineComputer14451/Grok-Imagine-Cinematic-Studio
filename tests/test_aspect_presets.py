"""Tests for aspect ratio presets and inline shot parsing."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from aspect_presets import (  # noqa: E402
    apply_aspect_to_shot,
    normalize_aspect,
    parse_aspect_from_spec,
    plan_social_variants,
)
from sfw_shots import parse_inline_shot  # noqa: E402


def test_normalize_aspect() -> None:
    assert normalize_aspect("9x16") == "9:16"
    assert normalize_aspect("invalid") == "16:9"
    assert normalize_aspect(None) == "16:9"


def test_parse_aspect_prefix() -> None:
    aspect, rest = parse_aspect_from_spec("9:16:hero:Cover shot")
    assert aspect == "9:16"
    assert rest == "hero:Cover shot"


def test_parse_aspect_embedded() -> None:
    aspect, rest = parse_aspect_from_spec("hero:9:16:Cover shot")
    assert aspect == "9:16"
    assert rest == "hero:Cover shot"


def test_parse_aspect_none_for_plain() -> None:
    aspect, rest = parse_aspect_from_spec("hero:Cover shot")
    assert aspect is None
    assert rest == "hero:Cover shot"


def test_inline_shot_with_aspect() -> None:
    shot = parse_inline_shot("9:16:hero:Vertical cover")
    assert shot["aspect_ratio"] == "9:16"
    assert shot["orientation"] == "portrait"
    assert shot["tier"] == "hero"
    assert "Vertical cover" in shot["description"]


def test_apply_aspect_handoff() -> None:
    shot = apply_aspect_to_shot({"tier": "hero"}, "1:1")
    assert shot["handoff_targets"]["key_art_designer"] == "instagram_poster"


def test_plan_social_variants() -> None:
    items = [
        {"shot_id": "a", "aspect_ratio": "16:9"},
        {"shot_id": "b", "aspect_ratio": "9:16"},
    ]
    plan = plan_social_variants(items)
    assert "16:9" in plan["formats"]
    assert "9:16" in plan["by_aspect"]


if __name__ == "__main__":
    test_normalize_aspect()
    test_parse_aspect_prefix()
    test_parse_aspect_embedded()
    test_parse_aspect_none_for_plain()
    test_inline_shot_with_aspect()
    test_apply_aspect_handoff()
    test_plan_social_variants()
    print("All aspect preset tests passed")