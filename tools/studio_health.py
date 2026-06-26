"""Shared studio workspace health metrics."""

from __future__ import annotations

from studio_paths import STUDIO_ROOT

SKILLS_ROOT = STUDIO_ROOT / ".grok" / "skills"
MIN_EXPECTED_SKILLS = 40


def count_skills() -> int:
    """Count skill directories with a SKILL.md manifest."""
    if not SKILLS_ROOT.is_dir():
        return 0
    return sum(1 for d in SKILLS_ROOT.iterdir() if (d / "SKILL.md").is_file())