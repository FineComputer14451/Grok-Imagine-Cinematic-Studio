"""NSFW sequence extension configuration — tension profiles, phases, camera, chain QA."""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "1.0"
NSFW_SEQUENCES_TAG = "nsfw_erotic_extension"

TENSION_PROFILES: dict[str, dict[str, Any]] = {
    "slow_burn": {
        "label": "Slow Burn",
        "clip_duration_range": (10, 14),
        "phase_weights": {
            "anticipation": 0.25,
            "approach": 0.20,
            "contact": 0.20,
            "escalation": 0.15,
            "peak": 0.12,
            "afterglow": 0.08,
        },
        "camera_style": "lingering holds, shallow DOF, minimal camera movement",
    },
    "passionate": {
        "label": "Passionate",
        "clip_duration_range": (8, 12),
        "phase_weights": {
            "anticipation": 0.15,
            "approach": 0.18,
            "contact": 0.22,
            "escalation": 0.22,
            "peak": 0.15,
            "afterglow": 0.08,
        },
        "camera_style": "push-ins on breath beats, orbit on contact, match cuts",
    },
    "intense": {
        "label": "Intense",
        "clip_duration_range": (6, 10),
        "phase_weights": {
            "anticipation": 0.10,
            "approach": 0.15,
            "contact": 0.25,
            "escalation": 0.25,
            "peak": 0.18,
            "afterglow": 0.07,
        },
        "camera_style": "handheld intimacy, whip-free closeups, rhythmic dolly pulses",
    },
}

EROTIC_PHASES: dict[str, dict[str, Any]] = {
    "anticipation": {
        "label": "Anticipation",
        "tension": 0.2,
        "motion_intensity": "low",
        "description": "Establish desire, proximity building, held breath",
    },
    "approach": {
        "label": "Approach",
        "tension": 0.4,
        "motion_intensity": "low-medium",
        "description": "First touch approaching, eye contact, micro-expressions",
    },
    "contact": {
        "label": "Contact",
        "tension": 0.55,
        "motion_intensity": "medium",
        "description": "Skin contact, fabric displacement begins, breath sync",
    },
    "escalation": {
        "label": "Escalation",
        "tension": 0.75,
        "motion_intensity": "medium-high",
        "description": "Intimate movement intensifies, weight transfer, momentum",
    },
    "peak": {
        "label": "Peak",
        "tension": 0.95,
        "motion_intensity": "high",
        "description": "Peak emotional intimacy beat — implied, R-rated, clothing on or tasteful suggestion",
    },
    "afterglow": {
        "label": "Afterglow",
        "tension": 0.35,
        "motion_intensity": "low",
        "description": "Deceleration, emotional residue, soft resolution",
    },
}

CAMERA_MOVES: dict[str, dict[str, Any]] = {
    "anticipation": {
        "primary": "static_hold",
        "options": ["slow_dolly_in", "subtle_crane_down", "rack_focus_eyes"],
        "lens": "50mm f/1.4",
        "framing": "medium close-up, negative space between bodies",
        "pacing_note": "Hold 3–4s before any camera move — let tension breathe",
    },
    "approach": {
        "primary": "slow_dolly_in",
        "options": ["orbit_15deg", "over_shoulder_intimate", "low_angle_up"],
        "lens": "35mm f/1.8",
        "framing": "over-shoulder or profile two-shot, shrinking distance",
        "pacing_note": "Dolly speed: 2cm/s — weighty, deliberate approach",
    },
    "contact": {
        "primary": "orbit_slow",
        "options": ["handheld_subtle", "macro_skin_detail", "match_cut_hands"],
        "lens": "85mm f/1.4",
        "framing": "close on contact point — hands, lips, collarbone",
        "pacing_note": "One primary contact per clip; avoid multi-focus",
    },
    "escalation": {
        "primary": "tracking_medium",
        "options": ["dolly_push_weight_transfer", "crane_reveal", "dutch_subtle"],
        "lens": "40mm anamorphic feel",
        "framing": "medium full, body lines visible, motivated shadows",
        "pacing_note": "Camera follows momentum vector — never fights body physics",
    },
    "peak": {
        "primary": "hero_push_in",
        "options": ["slow_motion_80pct", "extreme_close_texture", "silhouette_rim"],
        "lens": "50mm or 85mm — hero lens choice locked",
        "framing": "hero framing — single body focus or intimate two-shot",
        "pacing_note": "One unbroken 8–12s beat; no camera cuts within clip",
    },
    "afterglow": {
        "primary": "static_pull_back",
        "options": ["slow_dolly_out", "soft_focus_bloom", "window_light_shift"],
        "lens": "35mm f/2",
        "framing": "wider than peak — context returns, bodies at rest",
        "pacing_note": "Decelerate motion 40%; hold final 2s on emotional residue",
    },
}

NSFW_CHAIN_QA_CHECKS: tuple[tuple[str, str, float], ...] = (
    ("hand_finger_integrity", "Hands/fingers — no extra digits, natural pose", 1.4),
    ("skin_texture_consistency", "Skin detail — pores, tone, marks consistent at stitch", 1.3),
    ("fabric_cloth_physics", "Fabric interaction — drape, tension, displacement realistic", 1.2),
    ("explicit_area_artifact_risk", "Explicit zones — no morphing, duplication, uncanny detail", 1.5),
    ("body_proportion_stability", "Body proportions stable across stitch boundary", 1.3),
    ("intimate_physics_fidelity", "Weight transfer, skin deformation, momentum realistic", 1.4),
    ("erotic_tension_carryover", "Sensual tension curve maintained across boundary", 1.1),
    ("lighting_skin_modeling", "Motivated rim/practical light flatters skin at stitch", 1.0),
)

NSFW_QA_CRITICAL = frozenset({
    "hand_finger_integrity",
    "explicit_area_artifact_risk",
    "body_proportion_stability",
    "intimate_physics_fidelity",
})

ARTIFACT_AVOIDANCE_PROMPT_BLOCK = """Artifact Guard (explicit zones):
- Hands: single natural pose, fingers visible and anatomically correct, no merging
- Skin: consistent pore texture, no plastic sheen, no duplicate features
- Fabric: one primary tension point per clip, realistic drape and pull
- Bodies: stable proportions, no limb morphing at stitch boundary
- Physics: weighty momentum, skin compression on contact, hair response to movement"""