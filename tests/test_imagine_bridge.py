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
    build_handoff,
    build_reference_hints,
    build_sound_layer,
    handoff_steps,
    handoff_to_clipboard,
    handoff_to_markdown,
)
from models import (  # noqa: E402
    DEFAULT_IMAGINE_IMAGE_MODEL,
    DEFAULT_IMAGINE_VIDEO_MODEL,
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


def test_bridge_packet_defaults_to_studio_video_model() -> None:
    """No subject/arg video_model → STACK_CONTRACT cost default (1.0), not hardcoded 1.5."""
    packet = build_bridge_packet(
        {"shot_id": "shot_default", "description": "Establishing wide"},
        context="shot",
    )
    assert packet["video_model"] == DEFAULT_IMAGINE_VIDEO_MODEL
    assert packet["image_model"] == DEFAULT_IMAGINE_IMAGE_MODEL
    assert DEFAULT_IMAGINE_VIDEO_MODEL in packet["video_pipeline_spec"]
    assert "1.5" not in packet["video_model"]

    agent = build_agent_mode_handoff(
        {"shot_id": "shot_default", "prompt": "Establishing wide"},
        target_surface="grok_build_tools",
    )
    assert agent["video_model"] == DEFAULT_IMAGINE_VIDEO_MODEL
    assert agent["model_stack"]["imagine_video"] == DEFAULT_IMAGINE_VIDEO_MODEL
    assert agent["model_stack"]["imagine_image"] == DEFAULT_IMAGINE_IMAGE_MODEL


def test_bridge_packet_respects_explicit_1_5() -> None:
    packet = build_bridge_packet(
        {
            "shot_id": "shot_audio",
            "description": "Dialogue close-up",
            "video_model": "grok-imagine-video-1.5",
        },
        context="shot",
    )
    assert packet["video_model"] == "grok-imagine-video-1.5"
    assert "1.5" in packet["video_pipeline_spec"] or "grok-imagine-video-1.5" in packet[
        "video_pipeline_spec"
    ]


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


def test_agent_mode_handoff_invalid_mode_strict() -> None:
    """Agent-mode builder must not silently coerce unknown modes to video_prompt."""
    try:
        build_agent_mode_handoff(
            {"shot_id": "x", "prompt": "y", "recommended_mode": "not-a-real-mode"},
            target_surface="grok_build_tools",
        )
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "execution_mode" in str(exc)


def test_unified_build_handoff_wrappers() -> None:
    subject = {"shot_id": "s1", "description": "Wide", "recommended_mode": "i2v"}
    classic = build_handoff(subject, agent_mode=False)
    assert classic["mode"] == "image_to_video"
    assert "packet_type" not in classic

    agent = build_handoff(subject, target_surface="xai_api", agent_mode=True)
    assert agent["packet_type"] == "imagine_agent_mode_handoff"
    assert agent["execution_mode"] == "image_to_video"
    assert agent["target_surface"] == "xai_api"
    assert agent["handoff_steps"] == handoff_steps("xai_api", "image_to_video")


def test_unified_renderers_share_clipboard() -> None:
    packet = build_agent_mode_handoff(
        {
            "shot_id": "s1",
            "description": "Hero plate",
            "recommended_mode": "image_to_video",
            "video_model": "grok-imagine-video-1.5",
        },
        target_surface="grok_com_imagine",
    )
    clip = handoff_to_clipboard(packet)
    assert packet["prompt"] in clip
    assert "VIDEO_PIPELINE_SPEC" in clip or "grok-imagine-video" in clip
    # clipboard must come from the same packet (not a second classic rebuild)
    assert handoff_to_clipboard(packet) == bridge_to_clipboard(packet)
    md = handoff_to_markdown(packet)
    assert "Imagine Agent Mode Handoff" in md
    assert agent_mode_handoff_to_markdown(packet) == md


def test_agent_mode_image_defaults_to_image_2_0() -> None:
    packet = build_agent_mode_handoff(
        {"shot_id": "s_still", "description": "Hero key art", "recommended_mode": "still"},
        target_surface="xai_responses_tool",
    )
    assert packet["execution_mode"] == "image_prompt"
    assert packet["image_model"] == "grok-imagine-image-2.0"
    assert packet["model_stack"]["imagine_image"] == "grok-imagine-image-2.0"
    assert packet["target_surface"] == "xai_responses_tool"
    assert any("image_generation" in s for s in packet["handoff_steps"])


def test_agent_mode_web_steps_name_image_2_0() -> None:
    steps = handoff_steps("grok_com_imagine", "image_prompt")
    blob = " ".join(steps)
    assert "2.0" in blob or "Quality Mode" in blob


if __name__ == "__main__":
    test_build_sound_layer()
    test_reference_hints_locked()
    test_bridge_packet_shot()
    test_bridge_packet_clip()
    test_bridge_packet_defaults_to_studio_video_model()
    test_bridge_packet_respects_explicit_1_5()
    test_agent_mode_handoff_packet()
    test_agent_mode_handoff_invalid_surface()
    test_agent_mode_handoff_invalid_mode_strict()
    test_unified_build_handoff_wrappers()
    test_unified_renderers_share_clipboard()
    print("All imagine bridge tests passed")