from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ..deps import StudioBackend
from ..schemas.common import CliActionOut


# Streamlit/TUI parity action map
ACTION_ARGS: dict[str, list[str]] = {
    "doctor": ["doctor", "--quick"],
    "validate": ["validate"],
    "quota-sync": ["quota", "sync"],
    "models-verify": ["models", "verify"],
    "models": ["models", "verify"],
}


def run_cli_action(
    backend: StudioBackend,
    action: str,
    *,
    extra_args: list[str] | None = None,
    timeout_sec: int = 120,
) -> CliActionOut:
    key = action.strip().lower().replace("_", "-")
    base = ACTION_ARGS.get(key)
    if base is None:
        return CliActionOut(
            source="mock" if not backend.live else "live",
            studio_version="3.8.9",
            action=action,
            exit_code=2,
            output=f"Unknown action '{action}'. Allowed: {', '.join(sorted(ACTION_ARGS))}",
            ok=False,
        )

    args = [*base, *(extra_args or [])]
    if not backend.root or not backend.live:
        return _mock_cli(key, args)

    cli = backend.root / "tools" / "cinematic_studio_cli.py"
    if not cli.is_file():
        return _mock_cli(key, args)

    cmd = [sys.executable, str(cli), *args]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=str(backend.root),
        )
        out = ((result.stdout or "") + (result.stderr or "")).strip()
        return CliActionOut(
            source="live",
            studio_version="3.8.9",
            action=key,
            exit_code=int(result.returncode),
            output=out or "(no output)",
            ok=result.returncode == 0,
        )
    except subprocess.TimeoutExpired:
        return CliActionOut(
            source="live",
            studio_version="3.8.9",
            action=key,
            exit_code=124,
            output=f"Timed out after {timeout_sec}s",
            ok=False,
        )
    except Exception as exc:  # noqa: BLE001
        return CliActionOut(
            source="live",
            studio_version="3.8.9",
            action=key,
            exit_code=1,
            output=str(exc),
            ok=False,
        )


def _mock_cli(action: str, args: list[str]) -> CliActionOut:
    scripts = {
        "doctor": (
            0,
            "Studio doctor · OK\n· Role cards 23/23\n· Skills 52 loaded\n· Models stack compatible",
        ),
        "validate": (
            1,
            "validate · exit 1\n· PASS identity continuity\n· FAIL chain QA: alley-confrontation (1 no-go)",
        ),
        "quota-sync": (
            0,
            "quota sync · OK\n· Ledger aligned\n· Remaining 1840",
        ),
        "models-verify": (
            0,
            "models verify · OK\n· cinematic: grok-4.5\n· imagine video: 1.5",
        ),
        "models": (
            0,
            "models verify · OK\n· cinematic: grok-4.5\n· imagine video: 1.5",
        ),
    }
    code, out = scripts.get(action, (0, f"mock ok · {' '.join(args)}"))
    return CliActionOut(
        source="mock",
        studio_version="3.8.9",
        action=action,
        exit_code=code,
        output=out,
        ok=code == 0,
    )
