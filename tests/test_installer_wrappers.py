"""Temp-HOME smoke tests for VERSION pin + unified cinematic-studio wrapper."""

from __future__ import annotations

import os
import stat
import subprocess
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
COMMON = ROOT / "scripts" / "lib" / "cinematic_studio_common.sh"
WRAPPER_HELPER = ROOT / "scripts" / "lib" / "install_cli_wrappers.sh"
WRAPPER_TEMPLATE = ROOT / "scripts" / "wrappers" / "cinematic-studio"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def _run_bash(script: str, env: dict[str, str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd or ROOT),
        check=False,
    )


def test_wrapper_template_is_static_dispatcher() -> None:
    body = WRAPPER_TEMPLATE.read_text(encoding="utf-8")
    assert "install|update|verify|declutter" in body
    # Doctor is a Python CLI command (not meta installer)
    meta_branch = body.split("*)", 1)[0]
    assert "doctor" not in meta_branch.split("case", 1)[-1]
    assert "cinematic_studio_cli.py" in body
    assert "CINEMATIC_PROJECT_DIR" in body
    # No host-baked absolute project path
    assert "/home/" not in body


def test_install_wrappers_and_version_pin(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()

    # Minimal project tree the wrapper + version pin need
    (project / "scripts").mkdir()
    (project / "scripts" / "lib").mkdir()
    (project / "tools").mkdir()
    (project / "scripts" / "cinematic_studio.sh").write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env bash
            set -euo pipefail
            echo "meta:$1"
            """
        ),
        encoding="utf-8",
    )
    (project / "scripts" / "cinematic_studio.sh").chmod(
        (project / "scripts" / "cinematic_studio.sh").stat().st_mode | stat.S_IXUSR
    )
    (project / "tools" / "cinematic_studio_cli.py").write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import sys
            print("cli:" + " ".join(sys.argv[1:]))
            """
        ),
        encoding="utf-8",
    )

    env = {
        **os.environ,
        "HOME": str(home),
        "PROJECT_DIR": str(project),
        "CINEMATIC_PROJECT_DIR": str(project),
        "PATH": f"{home / '.grok' / 'bin'}:{home / '.local' / 'bin'}:{os.environ.get('PATH', '')}",
    }

    # Simulate install_tree VERSION pin + wrapper install
    script = textwrap.dedent(
        f"""\
        set -euo pipefail
        source "{COMMON}"
        source "{WRAPPER_HELPER}"
        CINEMATIC_SCRIPT_DIR="{ROOT / 'scripts'}"
        CINEMATIC_REPO_ROOT="{ROOT}"
        CINEMATIC_STUDIO_VERSION="{VERSION}"
        PROJECT_DIR="{project}"
        SKILLS_DIR="{home / '.grok' / 'skills'}"
        printf '%s\\n' "$CINEMATIC_STUDIO_VERSION" >"$PROJECT_DIR/VERSION"
        cinematic_studio_install_cli_wrappers
        """
    )
    result = _run_bash(script, env)
    assert result.returncode == 0, result.stderr + result.stdout

    version_file = (project / "VERSION").read_text(encoding="utf-8").strip()
    assert version_file == VERSION

    wrapper = home / ".grok" / "bin" / "cinematic-studio"
    assert wrapper.is_file()
    assert wrapper.stat().st_mode & stat.S_IXUSR
    assert (home / ".local" / "bin" / "cinematic-studio").is_symlink()
    # back-compat alias points at same dispatcher
    alias = home / ".grok" / "bin" / "cinematic-studio-install"
    assert alias.is_symlink() or alias.is_file()

    # Soft overwrite: second install does not create a new .bak when identical
    result2 = _run_bash(script, env)
    assert result2.returncode == 0, result2.stderr + result2.stdout
    assert "up to date" in result2.stdout
    assert not list((home / ".grok" / "bin").glob("cinematic-studio.bak.*"))

    # Meta subcommands route to shell installer
    meta = _run_bash(
        f'"{wrapper}" verify --plugin',
        env,
    )
    assert meta.returncode == 0, meta.stderr
    assert "meta:verify" in meta.stdout

    # Other args (including doctor) route to Python CLI
    cli = _run_bash(
        f'"{wrapper}" models verify',
        env,
    )
    assert cli.returncode == 0, cli.stderr
    assert "cli:models verify" in cli.stdout

    doctor = _run_bash(
        f'"{wrapper}" doctor --quick',
        env,
    )
    assert doctor.returncode == 0, doctor.stderr
    assert "cli:doctor --quick" in doctor.stdout

    # grok-doctor shim is installed next to the wrapper
    grok_doctor = home / ".grok" / "bin" / "grok-doctor"
    assert grok_doctor.is_file()


def test_wrapper_soft_backup_on_content_change(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    (project / "scripts" / "wrappers").mkdir(parents=True)
    (project / "tools").mkdir(parents=True)

    env = {
        **os.environ,
        "HOME": str(home),
        "PROJECT_DIR": str(project),
        "PATH": f"{home / '.grok' / 'bin'}:{os.environ.get('PATH', '')}",
    }

    bin_dir = home / ".grok" / "bin"
    bin_dir.mkdir(parents=True)
    dest = bin_dir / "cinematic-studio"
    dest.write_text("#!/usr/bin/env bash\necho old\n", encoding="utf-8")
    dest.chmod(dest.stat().st_mode | stat.S_IXUSR)

    script = textwrap.dedent(
        f"""\
        set -euo pipefail
        source "{WRAPPER_HELPER}"
        CINEMATIC_SCRIPT_DIR="{ROOT / 'scripts'}"
        CINEMATIC_REPO_ROOT="{ROOT}"
        PROJECT_DIR="{project}"
        cinematic_studio_install_cli_wrappers
        """
    )
    result = _run_bash(script, env)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "backup" in result.stdout.lower() or "Updating" in result.stdout
    backups = list(bin_dir.glob("cinematic-studio.bak.*"))
    assert len(backups) == 1
    assert "old" in backups[0].read_text(encoding="utf-8")
    assert "install|update|verify|declutter" in dest.read_text(encoding="utf-8")
