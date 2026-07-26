#!/usr/bin/env python3
"""
Ensure / update the official Grok Build CLI binary for Cinematic Studio.

Mirrors scripts/lib/install_cli_wrappers.sh (Method A install path) so the
Python CLI can install the binary without running a full studio install.

Official installer: https://x.ai/cli/install.sh
Min version: models.RECOMMENDED_GROK_BUILD_CLI_VERSION (0.2.93+)
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from models import (
    RECOMMENDED_GROK_BUILD_CLI_VERSION,
    _parse_grok_cli_version,
    cli_version_at_least,
    probe_grok_cli,
    version_tuple,
)

OFFICIAL_INSTALL_URL = os.environ.get(
    "CINEMATIC_GROK_INSTALL_URL", "https://x.ai/cli/install.sh"
)


def preferred_grok_paths() -> list[Path]:
    home = Path.home()
    return [
        home / ".grok" / "bin" / "grok",
        home / ".local" / "bin" / "grok",
    ]


def find_grok_binary() -> Path | None:
    """Prefer ~/.grok/bin/grok then ~/.local/bin/grok then PATH."""
    for p in preferred_grok_paths():
        if p.is_file() or p.is_symlink():
            try:
                if os.access(p, os.X_OK):
                    return p.resolve() if p.exists() else p
            except OSError:
                continue
    which = shutil.which("grok")
    return Path(which) if which else None


def probe_preferred() -> dict[str, Any]:
    """Probe preferred install location first, then PATH."""
    path = find_grok_binary()
    if path is None:
        return {
            "path": None,
            "version": None,
            "display": None,
            "raw": None,
            "ok": False,
            "min_version": RECOMMENDED_GROK_BUILD_CLI_VERSION,
            "meets_min": False,
        }
    # Prefer direct binary --version for accurate path
    try:
        result = subprocess.run(
            [str(path), "--version"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        blob = ((result.stdout or "") + (result.stderr or "")).strip()
    except (OSError, subprocess.TimeoutExpired):
        # Fall back to PATH probe
        p = probe_grok_cli()
        ver = p.get("version")
        meets = False
        if ver:
            try:
                meets = cli_version_at_least(str(ver), RECOMMENDED_GROK_BUILD_CLI_VERSION)
            except ValueError:
                meets = False
        return {
            **p,
            "ok": bool(p.get("path")),
            "min_version": RECOMMENDED_GROK_BUILD_CLI_VERSION,
            "meets_min": meets,
        }

    version = _parse_grok_cli_version(blob)

    meets = False
    if version:
        try:
            meets = cli_version_at_least(str(version), RECOMMENDED_GROK_BUILD_CLI_VERSION)
        except ValueError:
            meets = False
    display = blob.splitlines()[0] if blob else None
    return {
        "path": str(path),
        "version": version,
        "display": display,
        "raw": blob or None,
        "ok": True,
        "min_version": RECOMMENDED_GROK_BUILD_CLI_VERSION,
        "meets_min": meets,
    }


def _versioned_binary_key(path: Path) -> tuple[int, ...]:
    """Semver sort key for names like grok-0.2.112 (not lexicographic)."""
    ver = _parse_grok_cli_version(path.name) or "0.0.0"
    try:
        return version_tuple(ver)
    except ValueError:
        return (0, 0, 0)


def link_grok_binary() -> Path | None:
    """Ensure ~/.local/bin/grok points at ~/.grok/bin/grok when present."""
    home = Path.home()
    bin_dir = home / ".grok" / "bin"
    local_bin = home / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    local_bin.mkdir(parents=True, exist_ok=True)

    src = bin_dir / "grok"
    if not src.exists():
        # versioned binaries grok-0.2.112 — sort by semver, not string
        versions = sorted(bin_dir.glob("grok-[0-9]*"), key=_versioned_binary_key)
        if versions:
            latest = versions[-1]
            src.unlink(missing_ok=True)
            src.symlink_to(latest.name)
    if not src.exists():
        return None
    dest = local_bin / "grok"
    try:
        if dest.is_symlink() or dest.exists():
            dest.unlink()
        dest.symlink_to(src)
    except OSError:
        # non-fatal
        pass
    return src


def run_official_installer(url: str | None = None) -> dict[str, Any]:
    """curl|bash official installer. Returns {ok, message, detail, meets_min}."""
    install_url = url or OFFICIAL_INSTALL_URL
    if shutil.which("curl"):
        cmd = f'curl -fsSL "{install_url}" | bash'
    elif shutil.which("wget"):
        cmd = f'wget -qO- "{install_url}" | bash'
    else:
        return {
            "ok": False,
            "message": "need curl or wget for official installer",
            "detail": f"Manual: curl -fsSL {install_url} | bash",
            "meets_min": False,
        }
    try:
        result = subprocess.run(
            ["bash", "-lc", cmd],
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "ok": False,
            "message": f"installer failed: {exc}",
            "detail": "",
            "meets_min": False,
        }
    detail = ((result.stdout or "") + (result.stderr or "")).strip()
    link_grok_binary()
    probe = probe_preferred()
    meets = bool(probe.get("path") and probe.get("meets_min"))
    # Success requires binary present and ≥ min — not merely installer exit 0
    return {
        "ok": meets,
        "message": (
            f"official installer finished: {probe.get('version')} ({probe.get('path')})"
            if probe.get("path")
            else "official installer finished but binary still missing"
        ),
        "detail": detail[-4000:] if detail else "",
        "probe": probe,
        "meets_min": meets,
        "returncode": result.returncode,
    }


def run_grok_update(*, stable: bool = True) -> dict[str, Any]:
    """Run `grok update --stable` (or plain update) on preferred binary."""
    path = find_grok_binary()
    if path is None:
        return {"ok": False, "message": "grok binary not found", "detail": ""}
    args = [str(path), "update"]
    if stable:
        args.append("--stable")
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "message": f"grok update failed: {exc}", "detail": ""}
    detail = ((result.stdout or "") + (result.stderr or "")).strip()
    link_grok_binary()
    probe = probe_preferred()
    return {
        "ok": result.returncode == 0,
        "message": "grok update finished",
        "detail": detail[-4000:] if detail else "",
        "probe": probe,
        "returncode": result.returncode,
    }


def ensure_grok_build_cli(
    *,
    force: bool = False,
    min_version: str | None = None,
    skip: bool | None = None,
) -> dict[str, Any]:
    """
    Ensure Grok Build CLI ≥ min version.

    Policy (matches Method A install_cli_wrappers.sh):
      1. If skip env/flag → no-op
      2. If present and ≥ min and not force → OK + link
      3. If present → grok update --stable
      4. Else / still short → official installer
    """
    if skip is None:
        skip_env = os.environ.get("CINEMATIC_SKIP_GROK_CLI", "").strip().lower()
        skip = skip_env in ("1", "true", "yes")
    if skip:
        return {
            "ok": True,
            "skipped": True,
            "message": "skipped (CINEMATIC_SKIP_GROK_CLI)",
            "probe": probe_preferred(),
        }

    minimum = (
        min_version
        or os.environ.get("CINEMATIC_MIN_GROK_CLI")
        or RECOMMENDED_GROK_BUILD_CLI_VERSION
    )
    force = force or os.environ.get("CINEMATIC_FORCE_GROK_CLI", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )

    probe = probe_preferred()
    steps: list[str] = []

    if (
        not force
        and probe.get("path")
        and probe.get("version")
        and probe.get("meets_min")
    ):
        link_grok_binary()
        steps.append(f"OK {probe.get('version')} ≥ {minimum}")
        return {
            "ok": True,
            "skipped": False,
            "message": f"Grok Build CLI OK: {probe.get('version')} ≥ {minimum}",
            "probe": probe_preferred(),
            "steps": steps,
        }

    if probe.get("path"):
        steps.append("running grok update --stable")
        upd = run_grok_update(stable=True)
        steps.append(upd.get("message") or "update")
        probe = probe_preferred()
        if (
            upd.get("ok")
            and probe.get("version")
            and cli_version_at_least(str(probe["version"]), minimum)
        ):
            return {
                "ok": True,
                "skipped": False,
                "message": f"Grok Build CLI updated: {probe.get('version')}",
                "probe": probe,
                "steps": steps,
                "detail": upd.get("detail"),
            }
        steps.append("update insufficient; trying official installer")

    steps.append(f"running official installer ({OFFICIAL_INSTALL_URL})")
    inst = run_official_installer()
    steps.append(inst.get("message") or "install")
    probe = probe_preferred()
    meets = False
    if probe.get("version"):
        try:
            meets = cli_version_at_least(str(probe["version"]), minimum)
        except ValueError:
            meets = False
    ok = bool(probe.get("path") and meets)
    return {
        "ok": ok,
        "skipped": False,
        "message": (
            f"Grok Build CLI installed: {probe.get('version')} ({probe.get('path')})"
            if ok
            else (
                f"Grok Build CLI ensure finished but version "
                f"{probe.get('version') or 'missing'} < {minimum}"
                if probe.get("path")
                else "Grok Build CLI ensure finished but binary still missing"
            )
        ),
        "meets_min": meets,
        "probe": probe,
        "steps": steps,
        "detail": inst.get("detail"),
    }


def ensure_via_bash_lib(*, force: bool = False) -> dict[str, Any]:
    """
    Prefer the shell implementation (single source with Method A install).

    Falls back to pure-Python ``ensure_grok_build_cli`` if the lib is missing
    or the bash ensure process fails hard (timeout / OSError).
    """
    repo = Path(__file__).resolve().parent.parent
    lib = repo / "scripts" / "lib" / "install_cli_wrappers.sh"
    if not lib.is_file():
        result = ensure_grok_build_cli(force=force)
        result.setdefault("backend", "python")
        return result

    env = os.environ.copy()
    if force:
        env["CINEMATIC_FORCE_GROK_CLI"] = "1"
    # Source lib and call ensure
    script = f"""
set -euo pipefail
source "{lib}"
cinematic_studio_ensure_grok_build_cli
"""
    try:
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
            timeout=600,
            env=env,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        py = ensure_grok_build_cli(force=force)
        return {
            **py,
            "bash_error": str(exc),
            "backend": "python-fallback",
            "message": f"bash ensure failed ({exc}); {py.get('message')}",
        }
    detail = ((result.stdout or "") + (result.stderr or "")).strip()
    probe = probe_preferred()
    meets = bool(probe.get("meets_min"))
    ok = result.returncode == 0 and bool(probe.get("path")) and meets
    return {
        "ok": ok,
        "message": "bash cinematic_studio_ensure_grok_build_cli finished",
        "detail": detail[-4000:] if detail else "",
        "probe": probe,
        "meets_min": meets,
        "backend": "bash",
        "returncode": result.returncode,
    }
