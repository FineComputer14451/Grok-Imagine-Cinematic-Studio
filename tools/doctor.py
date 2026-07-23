"""
Grok Doctor — declarative health-check registry for Grok Build + Cinematic Studio.

Single source of truth used by:
  cinematic-studio doctor
  grok-doctor  (thin shell shim)
  python tools/cinematic_studio_cli.py doctor

Check implementations live in doctor_checks.py; types in doctor_types.py.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from doctor_checks import (
    check_api_keys,
    check_auth_and_config,
    check_catalog_pin,
    check_cinematic_studio_path,
    check_git,
    check_github_cli,
    check_grok_cli,
    check_model_stack,
    check_plugin_installed,
    check_pytest,
    check_quota_recon,
    check_skills_layout,
    check_verify_plugin,
    check_versions,
)
from doctor_types import (
    CheckResult,
    DoctorReport,
    exit_code,
    format_human_report,
    report_to_dict,
)
from studio_paths import STUDIO_ROOT

# Re-export public API for CLI / tests
__all__ = [
    "CheckResult",
    "CheckSpec",
    "DoctorContext",
    "DoctorReport",
    "REGISTRY",
    "check_auth_and_config",
    "check_grok_cli",
    "exit_code",
    "format_human_report",
    "report_to_dict",
    "run_doctor",
    "main",
]


@dataclass
class DoctorContext:
    """Shared inputs for registry runners."""

    home: Path
    repo_root: Path
    project_dir: Path
    include_release_pin: bool = True
    repo_version: str = "?"
    project_version: str = "?"


@dataclass(frozen=True)
class CheckSpec:
    """One entry in the doctor registry."""

    id: str
    run: Callable[[DoctorContext], list[CheckResult]]
    external: bool = False  # needs grok/gh/etc.
    full_only: bool = False  # skipped when quick=True


def _default_project_dir(home: Path) -> Path:
    env = os.environ.get("CINEMATIC_PROJECT_DIR", "").strip()
    if env:
        return Path(env).expanduser()
    return home / "Grok-Cinematic-Projects"


def resolve_repo_root(
    *,
    explicit: Path | str | None = None,
    studio_root: Path | None = None,
) -> Path:
    """Prefer explicit env/arg, else the installed tools tree (STUDIO_ROOT)."""
    if explicit:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("CINEMATIC_REPO_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return (studio_root or STUDIO_ROOT).resolve()


# ---------------------------------------------------------------------------
# Thin adapters: CheckSpec.run always receives DoctorContext
# ---------------------------------------------------------------------------


def _run_grok_cli(_ctx: DoctorContext) -> list[CheckResult]:
    return check_grok_cli()


def _run_cinematic_path(ctx: DoctorContext) -> list[CheckResult]:
    return check_cinematic_studio_path(repo_root=ctx.repo_root)


def _run_auth(ctx: DoctorContext) -> list[CheckResult]:
    return check_auth_and_config(home=ctx.home)


def _run_versions(ctx: DoctorContext) -> list[CheckResult]:
    checks, repo_v, proj_v = check_versions(
        repo_root=ctx.repo_root, project_dir=ctx.project_dir
    )
    ctx.repo_version = repo_v
    ctx.project_version = proj_v
    return checks


def _run_model_stack(_ctx: DoctorContext) -> list[CheckResult]:
    return check_model_stack()


def _run_plugin(ctx: DoctorContext) -> list[CheckResult]:
    expected = ctx.repo_version if ctx.repo_version != "?" else None
    return check_plugin_installed(expected_version=expected)


def _run_catalog(ctx: DoctorContext) -> list[CheckResult]:
    return check_catalog_pin(require_release=ctx.include_release_pin)


def _run_skills(ctx: DoctorContext) -> list[CheckResult]:
    return check_skills_layout(home=ctx.home, repo_root=ctx.repo_root)


def _run_verify_plugin(ctx: DoctorContext) -> list[CheckResult]:
    return check_verify_plugin(repo_root=ctx.repo_root)


def _run_git(ctx: DoctorContext) -> list[CheckResult]:
    return check_git(repo_root=ctx.repo_root)


def _run_api_keys(ctx: DoctorContext) -> list[CheckResult]:
    return check_api_keys(home=ctx.home)


def _run_github(_ctx: DoctorContext) -> list[CheckResult]:
    return check_github_cli()


def _run_pytest(ctx: DoctorContext) -> list[CheckResult]:
    return check_pytest(repo_root=ctx.repo_root)


def _run_quota_recon(_ctx: DoctorContext) -> list[CheckResult]:
    return check_quota_recon()


# ---------------------------------------------------------------------------
# Declarative registry — add checks here only.
# ---------------------------------------------------------------------------

REGISTRY: tuple[CheckSpec, ...] = (
    CheckSpec("grok_cli", _run_grok_cli, external=True),
    CheckSpec("cinematic_studio_path", _run_cinematic_path),
    CheckSpec("auth_config", _run_auth),
    CheckSpec("versions", _run_versions),
    CheckSpec("model_stack", _run_model_stack),
    CheckSpec("plugin_installed", _run_plugin, external=True),
    CheckSpec("catalog_pin", _run_catalog),
    CheckSpec("skills_layout", _run_skills),
    CheckSpec("verify_plugin", _run_verify_plugin, external=True, full_only=True),
    CheckSpec("git", _run_git),
    CheckSpec("api_keys", _run_api_keys),
    CheckSpec("github_cli", _run_github, external=True),
    CheckSpec("pytest", _run_pytest, external=True, full_only=True),
    CheckSpec("quota_recon", _run_quota_recon),
)


def run_doctor(
    *,
    quick: bool = False,
    home: Path | None = None,
    repo_root: Path | str | None = None,
    project_dir: Path | str | None = None,
    skip_external: bool = False,
    include_release_pin: bool = True,
) -> DoctorReport:
    """
    Run the declarative doctor registry.

    skip_external: omit checks marked external=True (no fake PASS rows).
    quick: omit checks marked full_only=True.
    """
    home_path = Path(home) if home is not None else Path.home()
    root = resolve_repo_root(explicit=repo_root)
    proj = (
        Path(project_dir).expanduser().resolve()
        if project_dir
        else _default_project_dir(home_path).resolve()
    )

    ctx = DoctorContext(
        home=home_path,
        repo_root=root,
        project_dir=proj,
        include_release_pin=include_release_pin,
    )
    report = DoctorReport(
        repo_root=str(root),
        project_dir=str(proj),
        quick=quick,
        started_at=datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    )

    for spec in REGISTRY:
        if quick and spec.full_only:
            continue
        if skip_external and spec.external:
            continue
        report.checks.extend(spec.run(ctx))

    report.repo_version = ctx.repo_version
    report.project_version = ctx.project_version
    return report


def main(argv: list[str] | None = None) -> int:
    """CLI entry for `python -m doctor` / direct execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Grok Doctor health check")
    parser.add_argument("--quick", "-q", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_out")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    report = run_doctor(quick=args.quick)
    if args.json_out:
        print(json.dumps(report_to_dict(report), indent=2))
    else:
        print(format_human_report(report))
    return exit_code(report, strict=args.strict)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
