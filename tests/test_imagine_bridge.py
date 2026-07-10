"""Tests for Imagine execution bridge."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from imagine_bridge import (  # noqa: E402
    PROTOCOL_VERSION,
    agent_mode_handoff_to_markdown,
    bridge_to_clipboard,
    bridge_to_markdown,
    build_agent_mode_handoff,
    build_bridge_packet,
    build_reference_hints,
    build_sound_layer,
)


def test_build_sound_layer() -> None:
    layer = build_sound_layer(dialogue="Hello there")
    assert "Sound Layer" in layer
    assert "Hello there" in layer


def test_reference_hints_locked() -> None:
    hints = build_reference_hints(reference_image_id="hero_001", lock_status="locked")
    assert any("hero_001" in h for h in hints)
    assert any("locked" in h for h in hints)


def test_bridge_packet_shot() -> None:
    shot = {
        "shot_id": "shot_hero_001",
        "tier": "hero",
        "description": "Cover frame at dusk",
        "recommended_mode": "image_to_video",
        "video_model": "grok-imagine-video-1.5",
        "image_model": "grok-imagine-image-quality",
        "reference_image_id": "plate_001",
        "aspect_ratio": "16:9",
    }
    packet = build_bridge_packet(shot, context="shot")
    assert "VIDEO_PIPELINE_SPEC" in packet["video_pipeline_spec"]
    assert packet["prompt"] == "Cover frame at dusk"
    assert packet["sound_layer"].startswith("Sound Layer")
    md = bridge_to_markdown(packet)
    assert "shot_hero_001" in md
    clip = bridge_to_clipboard(packet)
    assert "grok-imagine-video-1.5" in clip


def test_bridge_packet_clip() -> None:
    clip = {
        "clip_id": "clip_002",
        "prompt": "Continue dolly forward",
        "last_frame_recap": "Hero at window, rain on glass",
        "momentum_vector": {"last_action": "turns toward door"},
        "video_model": "grok-imagine-video-1.5",
    }
    packet = build_bridge_packet(clip, context="clip")
    assert packet["last_frame_recap"] == "Hero at window, rain on glass"
    assert "momentum_vector" in packet


def test_agent_mode_handoff_packet() -> None:
    shot = {
        "shot_id": "shot_hero_001",
        "description": "Cover frame at dusk",
        "recommended_mode": "image_to_video",
        "video_model": "grok-imagine-video-1.5",
        "image_model": "grok-imagine-image-quality",
        "reference_image_id": "plate_001",
        "aspect_ratio": "16:9",
    }
    packet = build_agent_mode_handoff(shot, target_surface="grok_build_tools", context="shot")
    assert packet["packet_type"] == "imagine_agent_mode_handoff"
    assert packet["protocol_version"] == PROTOCOL_VERSION
    assert packet["target_surface"] == "grok_build_tools"
    assert packet["execution_mode"] == "image_to_video"
    assert packet["prompt"] == "Cover frame at dusk"
    assert "VIDEO_PIPELINE_SPEC" in packet["video_pipeline_spec"]
    assert packet["sound_layer"].startswith("Sound Layer")
    assert packet["handoff_steps"]
    assert packet["return_path"]
    assert packet["quota_note"]
    md = agent_mode_handoff_to_markdown(packet)
    assert "Imagine Agent Mode Handoff" in md
    assert "shot_hero_001" in md


def test_agent_mode_handoff_invalid_surface() -> None:
    try:
        build_agent_mode_handoff({"shot_id": "x", "prompt": "y"}, target_surface="nope")
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "target_surface" in str(exc)


if __name__ == "__main__":
    test_build_sound_layer()
    test_reference_hints_locked()
    test_bridge_packet_shot()
    test_bridge_packet_clip()
    test_agent_mode_handoff_packet()
    test_agent_mode_handoff_invalid_surface()
    print("All imagine bridge tests passed")