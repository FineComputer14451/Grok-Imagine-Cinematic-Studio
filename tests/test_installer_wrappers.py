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
        # Unit tests must not hit the network for Grok Build install
        "CINEMATIC_SKIP_GROK_CLI": "1",
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
        "CINEMATIC_SKIP_GROK_CLI": "1",
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


def test_version_ge_and_parse_helpers() -> None:
    script = textwrap.dedent(
        f"""\
        set -euo pipefail
        source "{WRAPPER_HELPER}"
        cinematic_studio_version_ge "0.2.112" "0.2.93" || exit 11
        cinematic_studio_version_ge "0.2.93" "0.2.93" || exit 12
        cinematic_studio_version_ge "0.2.90" "0.2.93" && exit 13
        v="$(cinematic_studio_parse_grok_version 'grok 0.2.112 (9bbd) [stable]')"
        [[ "$v" == "0.2.112" ]] || exit 14
        """
    )
    result = _run_bash(script, {**os.environ})
    assert result.returncode == 0, result.stderr + result.stdout


def test_ensure_grok_cli_ok_when_binary_present(tmp_path: Path) -> None:
    """Fake grok binary meeting min version → ensure is a no-op (no network)."""
    home = tmp_path / "home"
    home.mkdir()
    bin_dir = home / ".grok" / "bin"
    bin_dir.mkdir(parents=True)
    fake = bin_dir / "grok"
    fake.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env bash
            if [[ "${1:-}" == "--version" ]]; then
              echo "grok 1.0.5 (deadbeef) [stable]"
              exit 0
            fi
            echo "unexpected: $*" >&2
            exit 2
            """
        ),
        encoding="utf-8",
    )
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)

    env = {
        **os.environ,
        "HOME": str(home),
        "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}",
        # Explicitly allow ensure; fake binary prevents network path
        "CINEMATIC_SKIP_GROK_CLI": "0",
        "CINEMATIC_MIN_GROK_CLI": "1.0.5",
    }
    script = textwrap.dedent(
        f"""\
        set -euo pipefail
        source "{WRAPPER_HELPER}"
        cinematic_studio_ensure_grok_build_cli
        """
    )
    result = _run_bash(script, env)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "Grok Build CLI OK" in result.stdout
    assert (home / ".local" / "bin" / "grok").is_symlink()


def _write(path: Path, text: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_copy_tools_tree_includes_tui_package(tmp_path: Path) -> None:
    src = tmp_path / "src_tools"
    project = tmp_path / "project"
    _write(src / "cinematic_studio_cli.py")
    _write(src / "cli" / "tui" / "__init__.py", "run_tui = None\n")
    _write(src / "cli" / "tui" / "widgets.py")

    env = {**os.environ, "PROJECT_DIR": str(project)}
    script = textwrap.dedent(
        f"""\
        set -euo pipefail
        source "{COMMON}"
        PROJECT_DIR="{project}"
        cinematic_studio_copy_tools_tree "{src}"
        """
    )
    result = _run_bash(script, env)
    assert result.returncode == 0, result.stderr + result.stdout
    assert (project / "tools" / "cli" / "tui" / "__init__.py").is_file()
    assert (project / "tools" / "cli" / "tui" / "widgets.py").is_file()
    assert (project / "tools" / "cinematic_studio_cli.py").is_file()


def test_install_tree_copies_studio_core_and_tui(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    project = tmp_path / "project"
    home = tmp_path / "home"
    skills_dir = home / ".grok" / "skills"

    _write(bundle / ".grok" / "skills" / "studio-director" / "SKILL.md", "# studio-director\n")
    for name in (
        "cinematic_studio_cli.py",
        "models.py",
        "grok_build_cli.py",
    ):
        _write(bundle / "tools" / name)
    for name in ("models_commands.py", "grok_cli_commands.py", "wave_a_commands.py"):
        _write(bundle / "tools" / "cli" / name)
    _write(bundle / "tools" / "cli" / "tui" / "__init__.py")
    _write(bundle / "studio_core" / "__init__.py")
    _write(bundle / "studio_core" / "services" / "dashboard.py", "def build_studio_dashboard():\n    return {}\n")
    _write(bundle / "VERSION", VERSION + "\n")
    _write(bundle / "references" / "MODELS.md", "# models\n")

    env = {
        **os.environ,
        "HOME": str(home),
        "PROJECT_DIR": str(project),
        "CINEMATIC_SKIP_GROK_CLI": "1",
        "PATH": f"{home / '.grok' / 'bin'}:{home / '.local' / 'bin'}:{os.environ.get('PATH', '')}",
    }
    script = textwrap.dedent(
        f"""\
        set -euo pipefail
        source "{COMMON}"
        source "{WRAPPER_HELPER}"
        CINEMATIC_SCRIPT_DIR="{ROOT / 'scripts'}"
        CINEMATIC_REPO_ROOT="{ROOT}"
        CINEMATIC_STUDIO_VERSION="{VERSION}"
        PROJECT_DIR="{project}"
        SKILLS_DIR="{skills_dir}"
        cinematic_studio_install_tree "{bundle}"
        cinematic_studio_tools_complete
        """
    )
    result = _run_bash(script, env)
    assert result.returncode == 0, result.stderr + result.stdout
    assert (skills_dir / "studio-director" / "SKILL.md").is_file()
    assert (project / "studio_core" / "services" / "dashboard.py").is_file()
    assert (project / "tools" / "cli" / "tui" / "__init__.py").is_file()
    assert (project / "VERSION").read_text(encoding="utf-8").strip() == VERSION


def test_tools_complete_fails_without_studio_core(tmp_path: Path) -> None:
    project = tmp_path / "project"
    for rel in (
        "tools/cinematic_studio_cli.py",
        "tools/models.py",
        "tools/grok_build_cli.py",
        "tools/cli/models_commands.py",
        "tools/cli/grok_cli_commands.py",
        "tools/cli/wave_a_commands.py",
        "tools/cli/tui/__init__.py",
    ):
        _write(project / rel)

    env = {**os.environ, "PROJECT_DIR": str(project)}
    script = textwrap.dedent(
        f"""\
        set -euo pipefail
        source "{COMMON}"
        PROJECT_DIR="{project}"
        cinematic_studio_tools_complete && exit 11
        mkdir -p "$PROJECT_DIR/studio_core/services"
        printf 'x\\n' >"$PROJECT_DIR/studio_core/services/dashboard.py"
        cinematic_studio_tools_complete || exit 12
        """
    )
    result = _run_bash(script, env)
    assert result.returncode == 0, result.stderr + result.stdout


def test_resolve_python_prefers_project_venv(tmp_path: Path) -> None:
    project = tmp_path / "project"
    venv_py = project / ".venv" / "bin" / "python"
    _write(venv_py, "#!/usr/bin/env bash\necho venv\n")
    venv_py.chmod(venv_py.stat().st_mode | stat.S_IXUSR)

    env = {**os.environ, "PROJECT_DIR": str(project)}
    env.pop("CINEMATIC_PYTHON", None)
    script = textwrap.dedent(
        f"""\
        set -euo pipefail
        source "{COMMON}"
        PROJECT_DIR="{project}"
        unset CINEMATIC_PYTHON || true
        py="$(cinematic_studio_resolve_python)"
        [[ "$py" == "{venv_py}" ]]
        """
    )
    result = _run_bash(script, env)
    assert result.returncode == 0, result.stderr + result.stdout


def test_print_next_steps_does_not_clobber_existing_config(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    grok = home / ".grok"
    grok.mkdir(parents=True)
    (grok / "config.toml").write_text("keep-me\n", encoding="utf-8")
    _write(project / "config" / "grok-build.example.toml", "example\n")
    _write(project / "tools" / "cinematic_studio_cli.py")

    env = {
        **os.environ,
        "HOME": str(home),
        "PROJECT_DIR": str(project),
    }
    script = textwrap.dedent(
        f"""\
        set -euo pipefail
        source "{COMMON}"
        PROJECT_DIR="{project}"
        HOME="{home}"
        CINEMATIC_STUDIO_VERSION="{VERSION}"
        cinematic_studio_print_next_steps
        """
    )
    result = _run_bash(script, env)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "already exists" in result.stdout
    assert "cp " not in result.stdout.split("already exists")[-1]
    assert (grok / "config.toml").read_text(encoding="utf-8") == "keep-me\n"
