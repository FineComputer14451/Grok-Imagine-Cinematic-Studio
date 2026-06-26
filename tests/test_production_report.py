"""Tests for unified production report."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from production_report import build_production_report, report_to_markdown  # noqa: E402


def test_build_production_report_shape() -> None:
    report = build_production_report()
    assert "quota" in report
    assert "batches" in report
    assert "imagine_jobs" in report
    assert "artifacts" in report
    assert "generated_at" in report


def test_report_markdown() -> None:
    report = build_production_report()
    md = report_to_markdown(report)
    assert "# Production Report" in md
    assert "Quota" in md


if __name__ == "__main__":
    test_build_production_report_shape()
    test_report_markdown()
    print("All production report tests passed")