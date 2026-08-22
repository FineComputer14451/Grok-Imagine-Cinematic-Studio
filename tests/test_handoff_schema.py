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
    resolve_execution_mode,
)
from imagine_bridge import (  # noqa: E402
    EXECUTION_MODES as BRIDGE_MODES,
    TARGET_SURFACES as BRIDGE_SURFACES,
    PROTOCOL_VERSION as BRIDGE_PROTOCOL,
    handoff_steps,
)
from models import STUDIO_COMPATIBILITY_VERSION  # noqa: E402


def test_surfaces_and_modes_nonempty() -> None:
    assert len(TARGET_SURFACES) == 5
    assert "grok_build_tools" in TARGET_SURFACES
    assert "xai_responses_tool" in TARGET_SURFACES
    assert len(EXECUTION_MODES) >= 7
    assert "video_edit" in EXECUTION_MODES
    assert "video_extend" in EXECUTION_MODES
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


def test_resolve_execution_mode_aliases_for_spend_gates() -> None:
    """Batch shorthand must map so plate/motion gates do not silently skip."""
    assert resolve_execution_mode({"recommended_mode": "i2v"}) == "image_to_video"
    assert resolve_execution_mode({"recommended_mode": "I2V"}) == "image_to_video"
    assert resolve_execution_mode({"decision": {"mode": "still"}}) == "image_prompt"
    assert resolve_execution_mode({"execution_mode": "video"}) == "video_prompt"
    assert resolve_execution_mode({}, execution_mode="image") == "image_prompt"
    # Empty must not invent video_prompt (would false-trigger motion gates).
    assert resolve_execution_mode({}) == ""
    assert resolve_execution_mode({"recommended_mode": ""}) == ""
    # Unknown kept as-is (soft).
    assert resolve_execution_mode({"recommended_mode": "not-a-mode"}) == "not-a-mode"


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
    assert normalize_target_surface("grok_mobile_imagine") == "grok_com_imagine"
    assert normalize_target_surface("responses") == "xai_responses_tool"
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


def test_protocol_version_tracks_studio() -> None:
    assert PROTOCOL_VERSION == STUDIO_COMPATIBILITY_VERSION
    assert BRIDGE_PROTOCOL == STUDIO_COMPATIBILITY_VERSION


def test_handoff_steps_for_all_surfaces() -> None:
    for surface in sorted(TARGET_SURFACES):
        for mode in ("image_prompt", "image_to_video", "video_prompt", "video_edit", "video_extend"):
            steps = handoff_steps(surface, mode)
            assert isinstance(steps, list) and len(steps) >= 3
            assert all(isinstance(s, str) and s.strip() for s in steps)


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
