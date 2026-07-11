"""Tests for canonical Imagine Agent Mode handoff schema."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from handoff_schema import (  # noqa: E402
    CANONICAL_PROTOCOL_DOC,
    EXECUTION_MODES,
    PACKET_TYPE_IMAGINE_AGENT_MODE,
    PROTOCOL_VERSION,
    TARGET_SURFACES,
    VIDEO_EXECUTION_MODES,
    imagine_agent_mode_packet_schema,
    is_video_execution_mode,
    normalize_execution_mode,
    normalize_target_surface,
)
from imagine_bridge import (  # noqa: E402
    EXECUTION_MODES as BRIDGE_MODES,
    TARGET_SURFACES as BRIDGE_SURFACES,
    PROTOCOL_VERSION as BRIDGE_PROTOCOL,
)


def test_surfaces_and_modes_nonempty() -> None:
    assert len(TARGET_SURFACES) == 4
    assert "grok_build_tools" in TARGET_SURFACES
    assert len(EXECUTION_MODES) >= 5
    assert VIDEO_EXECUTION_MODES <= EXECUTION_MODES


def test_bridge_reexports_same_objects() -> None:
    """CLI imports from imagine_bridge must not drift from handoff_schema."""
    assert BRIDGE_SURFACES == TARGET_SURFACES
    assert BRIDGE_MODES == EXECUTION_MODES
    assert BRIDGE_PROTOCOL == PROTOCOL_VERSION


def test_normalize_execution_mode_aliases() -> None:
    assert normalize_execution_mode("i2v") == "image_to_video"
    assert normalize_execution_mode("still") == "image_prompt"
    assert normalize_execution_mode("video") == "video_prompt"
    assert normalize_execution_mode(None) == "video_prompt"


def test_normalize_execution_mode_strict() -> None:
    try:
        normalize_execution_mode("not-a-mode", strict=True)
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "execution_mode" in str(exc)


def test_normalize_execution_mode_soft_fallback() -> None:
    assert normalize_execution_mode("not-a-mode", strict=False) == "video_prompt"


def test_normalize_target_surface() -> None:
    assert normalize_target_surface("xai_api") == "xai_api"
    try:
        normalize_target_surface("nope")
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "target_surface" in str(exc)


def test_is_video_execution_mode() -> None:
    assert is_video_execution_mode("image_to_video")
    assert is_video_execution_mode("video_prompt")
    assert not is_video_execution_mode("image_prompt")


def test_packet_schema_fragment() -> None:
    schema = imagine_agent_mode_packet_schema()
    assert schema["target_surfaces"] is TARGET_SURFACES or schema["target_surfaces"] == TARGET_SURFACES
    assert schema["execution_modes"] == EXECUTION_MODES
    assert schema["video_modes"] == VIDEO_EXECUTION_MODES
    assert "subject_id" in schema["required"]
    assert "video_pipeline_spec" in schema["video_required"]


def test_packet_type_constant() -> None:
    assert PACKET_TYPE_IMAGINE_AGENT_MODE == "imagine_agent_mode_handoff"


def test_canonical_protocol_doc_is_single_source() -> None:
    """Full protocol lives under references/agents/; skill copies are pointers only."""
    canonical = ROOT / CANONICAL_PROTOCOL_DOC
    assert canonical.is_file()
    body = canonical.read_text(encoding="utf-8")
    assert "Imagine Agent Mode Handoff" in body
    assert len(body) > 2000  # full protocol, not a stub

    pointers = [
        ROOT
        / ".grok/skills/studio-director/references/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md",
        ROOT
        / ".grok/skills/grok-imagine-cinematic-studio/references/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md",
    ]
    for path in pointers:
        assert path.is_file(), path
        text = path.read_text(encoding="utf-8")
        assert "pointer" in text.lower() or "Canonical source" in text
        assert "references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md" in text
        # Must not re-duplicate the full protocol
        assert len(text) < 1500
