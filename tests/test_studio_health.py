"""Tests for shared studio health metrics."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from studio_health import MIN_EXPECTED_SKILLS, count_skills  # noqa: E402


def test_count_skills_positive() -> None:
    assert count_skills() >= MIN_EXPECTED_SKILLS


if __name__ == "__main__":
    test_count_skills_positive()
    print("All studio health tests passed")