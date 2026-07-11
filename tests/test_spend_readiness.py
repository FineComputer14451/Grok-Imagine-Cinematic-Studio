"""Generation spend readiness facade (plate + motion)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from spend_readiness import (  # noqa: E402
    evaluate_generation_spend_readiness,
    spend_hard_fail_reasons,
)


def test_i2v_missing_plate_and_motion_fails_children() -> None:
    r = evaluate_generation_spend_readiness(
        {"recommended_mode": "image_to_video", "prompt": "static person"},
        strict_motion=False,
    )
    assert r["plate"]["pass"] is False
    assert r["motion"]["pass"] is False
    assert r["pass"] is False
    assert spend_hard_fail_reasons(r, strict_plate=False, strict_motion=False) == []
    assert "plate" in spend_hard_fail_reasons(r, strict_plate=True, strict_motion=False)
    assert "motion" in spend_hard_fail_reasons(r, strict_plate=False, strict_motion=True)


def test_ready_shot_passes() -> None:
    r = evaluate_generation_spend_readiness(
        {
            "recommended_mode": "image_to_video",
            "plate_status": "locked",
            "reference_image_id": "p1",
            "motion_vector": {
                "action": "turns",
                "camera": "dolly",
                "emotion": "calm",
            },
            "motion_tier": "medium",
            "prompt": "ignored when triple present",
        },
        strict_motion=True,
    )
    assert r["pass"] is True
    assert spend_hard_fail_reasons(r, strict_plate=True, strict_motion=True) == []
