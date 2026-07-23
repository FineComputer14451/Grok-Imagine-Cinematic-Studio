"""Shared types and report helpers for Grok Doctor."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

Status = Literal["PASS", "FAIL", "WARN"]


@dataclass(frozen=True)
class CheckResult:
    status: Status
    name: str
    detail: str
    section: str = ""


@dataclass
class DoctorReport:
    checks: list[CheckResult] = field(default_factory=list)
    repo_version: str = "?"
    project_version: str = "?"
    repo_root: str = ""
    project_dir: str = ""
    quick: bool = False
    started_at: str = ""

    @property
    def pass_count(self) -> int:
        return sum(1 for c in self.checks if c.status == "PASS")

    @property
    def fail_count(self) -> int:
        return sum(1 for c in self.checks if c.status == "FAIL")

    @property
    def warn_count(self) -> int:
        return sum(1 for c in self.checks if c.status == "WARN")

    @property
    def healthy(self) -> bool:
        return self.fail_count == 0


def exit_code(report: DoctorReport, *, strict: bool = False) -> int:
    """Return process exit code for a doctor report."""
    if report.fail_count > 0:
        return 1
    if strict and report.warn_count > 0:
        return 1
    return 0


def report_to_dict(report: DoctorReport) -> dict[str, Any]:
    """Machine-readable summary (stable keys for scripts/CI)."""
    return {
        "pass": report.pass_count,
        "fail": report.fail_count,
        "warn": report.warn_count,
        "repo_version": report.repo_version,
        "project_version": report.project_version,
        "repo_root": report.repo_root,
        "project_dir": report.project_dir,
        "quick": report.quick,
        "started_at": report.started_at,
        "healthy": report.healthy,
        "checks": [
            {
                "status": c.status,
                "name": c.name,
                "detail": c.detail,
                "section": c.section,
            }
            for c in report.checks
        ],
    }


def format_human_report(report: DoctorReport) -> str:
    """Render the classic Grok Doctor human summary."""
    lines: list[str] = [
        "════════════════════════════════════════",
        f" GROK DOCTOR · {report.started_at or datetime.now().isoformat(timespec='seconds')}",
        " Studio doctor for Grok Build + Cinematic Studio",
        "════════════════════════════════════════",
    ]

    current_section = ""
    icons = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️ "}
    for check in report.checks:
        if check.section and check.section != current_section:
            current_section = check.section
            lines.append("")
            lines.append(f"── {current_section} ──")
        icon = icons.get(check.status, "•")
        lines.append(f"  {icon} {check.name} — {check.detail}")

    lines.extend(
        [
            "",
            "════════════════════════════════════════",
            " SUMMARY",
            "════════════════════════════════════════",
            (
                f"  ✅ pass: {report.pass_count}   ❌ fail: {report.fail_count}   "
                f"⚠️  warn: {report.warn_count}"
            ),
        ]
    )
    if report.healthy:
        lines.append("  Verdict: HEALTHY")
        ver = report.repo_version if report.repo_version != "?" else "3.8.x"
        lines.append(f"  Activate: Activate Grok Imagine Cinematic Studio v{ver}")
    else:
        lines.append("  Verdict: NEEDS ATTENTION")
    lines.append("════════════════════════════════════════")
    return "\n".join(lines)
