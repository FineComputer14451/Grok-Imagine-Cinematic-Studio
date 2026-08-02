"""Safe action execution for CLI/TUI/Web/API shells.

Validates ActionSpec answers, builds argv, then runs either:
  - ``subprocess`` — isolated process (default for Textual TUI)
  - ``inprocess``  — Typer app invoke in-process (Web/API; no process spawn)

Forbidden argv tokens are always rejected. Free-form argv is never accepted
via :func:`execute_action` (only registered action ids).
"""

from __future__ import annotations

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from concurrent.futures import TimeoutError as FuturesTimeout
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from studio_core.pathutil import STUDIO_ROOT, ensure_import_paths
from studio_core.services.actions import (
    answers_to_argv,
    reject_forbidden_argv,
    static_allowed_argvs,
    validate_answers,
)

ExecuteMode = Literal["inprocess", "subprocess"]


@dataclass(frozen=True)
class ActionResult:
    """Result of :func:`execute_action` / :func:`execute_argv`."""

    ok: bool
    argv: list[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""
    errors: list[str] = field(default_factory=list)
    timed_out: bool = False
    action_id: str | None = None
    mode: str = "inprocess"

    @property
    def output(self) -> str:
        """Combined stdout+stderr for simple UI display."""
        if self.stdout and self.stderr:
            return self.stdout.rstrip() + "\n" + self.stderr
        return self.stdout or self.stderr


def resolve_repo_root(cwd: Path | None = None) -> Path:
    """Project root containing tools/cinematic_studio_cli.py."""
    env = os.environ.get("CINEMATIC_PROJECT_DIR")
    if env:
        candidate = Path(env).expanduser().resolve()
        if (candidate / "tools" / "cinematic_studio_cli.py").is_file():
            return candidate
    if cwd is not None:
        c = Path(cwd).resolve()
        if (c / "tools" / "cinematic_studio_cli.py").is_file():
            return c
    # Prefer pathutil root when it looks like a checkout
    if (STUDIO_ROOT / "tools" / "cinematic_studio_cli.py").is_file():
        return STUDIO_ROOT
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "tools" / "cinematic_studio_cli.py").is_file():
            return parent
    return STUDIO_ROOT


def cli_script_path(cwd: Path | None = None) -> Path:
    return resolve_repo_root(cwd) / "tools" / "cinematic_studio_cli.py"


def _deny(
    argv: list[str],
    message: str,
    *,
    action_id: str | None = None,
    mode: str = "inprocess",
    errors: list[str] | None = None,
) -> ActionResult:
    errs = list(errors) if errors is not None else [message]
    return ActionResult(
        ok=False,
        argv=list(argv),
        returncode=2,
        stdout="",
        stderr=message,
        errors=errs,
        timed_out=False,
        action_id=action_id,
        mode=mode,
    )


def _subprocess_run(
    argv: list[str],
    *,
    timeout: float,
    cwd: Path | None,
    action_id: str | None,
) -> ActionResult:
    if not argv:
        return _deny([], "No command argv provided.", action_id=action_id, mode="subprocess")

    try:
        reject_forbidden_argv(argv)
    except ValueError as exc:
        return _deny(argv, str(exc), action_id=action_id, mode="subprocess", errors=[str(exc)])

    script = cli_script_path(cwd)
    if not script.is_file():
        msg = f"CLI script not found: {script}"
        return _deny(argv, msg, action_id=action_id, mode="subprocess", errors=[msg])

    workdir = cwd or resolve_repo_root(cwd)
    cmd = [sys.executable, str(script), *argv]
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(workdir),
            timeout=max(1.0, float(timeout)),
        )
        code = int(completed.returncode)
        return ActionResult(
            ok=code == 0,
            argv=list(argv),
            returncode=code,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            errors=[] if code == 0 else [f"exit {code}"],
            timed_out=False,
            action_id=action_id,
            mode="subprocess",
        )
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        err = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        msg = f"Command timed out after {timeout}s: {' '.join(argv)}"
        return ActionResult(
            ok=False,
            argv=list(argv),
            returncode=124,
            stdout=out,
            stderr=(err + "\n" + msg).strip(),
            errors=[msg],
            timed_out=True,
            action_id=action_id,
            mode="subprocess",
        )


_CLI_APP: Any = None
_INPROCESS_LOCK = Lock()


def _load_cli_app() -> Any:
    """Load the Typer app from tools/cinematic_studio_cli.py (cached)."""
    global _CLI_APP
    if _CLI_APP is not None:
        return _CLI_APP

    ensure_import_paths()
    import importlib.util

    path = cli_script_path()
    if not path.is_file():
        raise FileNotFoundError(f"CLI script not found: {path}")

    spec = importlib.util.spec_from_file_location("cinematic_studio_cli_mod", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load CLI from {path}")
    mod = importlib.util.module_from_spec(spec)
    # Register under a stable name so relative imports inside behave
    sys.modules.setdefault("cinematic_studio_cli_mod", mod)
    spec.loader.exec_module(mod)
    app = getattr(mod, "app", None)
    if app is None:
        raise ImportError("cinematic_studio_cli.py has no 'app' Typer instance")
    _CLI_APP = app
    return _CLI_APP


def _invoke_typer(argv: list[str], *, cwd: Path) -> tuple[int, str, str]:
    """Invoke Typer app in-process; return (code, stdout, stderr)."""
    from typer.testing import CliRunner

    app = _load_cli_app()
    runner = CliRunner()
    # Click 8+: stderr captured separately when mix_stderr not used
    # Serialize: CliRunner/chdir are not concurrent-safe (NiceGUI multi-click).
    with _INPROCESS_LOCK:
        prev = os.getcwd()
        try:
            os.chdir(str(cwd))
            result = runner.invoke(app, argv, catch_exceptions=True)
        finally:
            os.chdir(prev)

        code = int(result.exit_code if result.exit_code is not None else 1)
        out = result.stdout or ""
        err = getattr(result, "stderr", None) or ""
        if result.exception is not None and not err:
            err = f"{type(result.exception).__name__}: {result.exception}"
        return code, out, err


def _inprocess_run(
    argv: list[str],
    *,
    timeout: float,
    cwd: Path | None,
    action_id: str | None,
) -> ActionResult:
    if not argv:
        return _deny([], "No command argv provided.", action_id=action_id, mode="inprocess")

    try:
        reject_forbidden_argv(argv)
    except ValueError as exc:
        return _deny(argv, str(exc), action_id=action_id, mode="inprocess", errors=[str(exc)])

    workdir = cwd or resolve_repo_root(cwd)
    timeout = max(1.0, float(timeout))

    def _call() -> tuple[int, str, str]:
        return _invoke_typer(argv, cwd=workdir)

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(_call)
            code, out, err = fut.result(timeout=timeout)
    except FuturesTimeout:
        msg = f"Command timed out after {timeout}s: {' '.join(argv)}"
        return ActionResult(
            ok=False,
            argv=list(argv),
            returncode=124,
            stdout="",
            stderr=msg,
            errors=[msg],
            timed_out=True,
            action_id=action_id,
            mode="inprocess",
        )
    except Exception as exc:  # noqa: BLE001
        msg = f"In-process invoke failed: {exc}"
        return ActionResult(
            ok=False,
            argv=list(argv),
            returncode=1,
            stdout="",
            stderr=msg,
            errors=[msg],
            timed_out=False,
            action_id=action_id,
            mode="inprocess",
        )

    return ActionResult(
        ok=code == 0,
        argv=list(argv),
        returncode=code,
        stdout=out,
        stderr=err,
        errors=[] if code == 0 else [f"exit {code}"],
        timed_out=False,
        action_id=action_id,
        mode="inprocess",
    )


def execute_argv(
    argv: list[str],
    *,
    mode: ExecuteMode = "inprocess",
    timeout: float = 60.0,
    cwd: Path | None = None,
    action_id: str | None = None,
    require_static_allowlist: bool = False,
) -> ActionResult:
    """Execute a fully-built argv with forbidden-token checks.

    When ``require_static_allowlist`` is True (TUI static launcher path),
    only field-less registered argvs are allowed.
    """
    if require_static_allowlist:
        key = tuple(argv)
        if key not in static_allowed_argvs():
            msg = "argv not in TUI static allowlist; use execute_action(action_id, answers)."
            return _deny(argv, msg, action_id=action_id, mode=mode, errors=[msg])

    if mode == "subprocess":
        return _subprocess_run(argv, timeout=timeout, cwd=cwd, action_id=action_id)
    if mode == "inprocess":
        return _inprocess_run(argv, timeout=timeout, cwd=cwd, action_id=action_id)
    return _deny(
        argv,
        f"Unknown execute mode: {mode!r} (use 'inprocess' or 'subprocess')",
        action_id=action_id,
        mode=str(mode),
    )


def execute_action(
    action_id: str,
    answers: dict[str, str] | None = None,
    *,
    mode: ExecuteMode = "inprocess",
    timeout: float = 60.0,
    cwd: Path | None = None,
) -> ActionResult:
    """Validate answers, build argv from ActionSpec, and execute.

    Parameters
    ----------
    action_id:
        Registered id from ``studio_core.services.actions.ACTIONS``.
    answers:
        Form field values (stringly-typed, same as TUI forms).
    mode:
        ``inprocess`` (Web/API default) or ``subprocess`` (TUI isolation).
    timeout:
        Seconds before the run is aborted (both modes).
    cwd:
        Working directory; defaults to studio repo root.
    """
    ans = answers or {}
    errors = validate_answers(action_id, ans)
    if errors:
        msg = "Validation failed: " + "; ".join(errors)
        return _deny([], msg, action_id=action_id, mode=mode, errors=errors)

    try:
        argv = answers_to_argv(action_id, ans)
    except (ValueError, KeyError) as exc:
        return _deny([], str(exc), action_id=action_id, mode=mode, errors=[str(exc)])

    return execute_argv(
        argv,
        mode=mode,
        timeout=timeout,
        cwd=cwd,
        action_id=action_id,
        require_static_allowlist=False,
    )
