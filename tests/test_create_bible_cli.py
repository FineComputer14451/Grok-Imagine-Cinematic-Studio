"""CLI create-bible direct path, help, non-TTY policy, and wizard with injected input."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools" / "cinematic_studio_cli.py"
sys.path.insert(0, str(ROOT / "tools"))

from cli.bible_wizard_cli import run_bible_wizard  # noqa: E402
from test_production_bible import REQUIRED_BIBLE_KEYS  # noqa: E402


def run_cli(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
        input=stdin,
    )


def test_create_bible_help_lists_wizard() -> None:
    result = run_cli("create-bible", "--help")
    assert result.returncode == 0, result.stderr
    assert "--wizard" in result.stdout
    assert "-w" in result.stdout


def test_create_bible_direct_writes_compatible_json(tmp_path: Path) -> None:
    out = tmp_path / "bible.json"
    result = run_cli(
        "create-bible",
        "CLI Direct Smoke",
        "--genre",
        "Sci-Fi",
        "-o",
        str(out),
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert out.is_file()
    bible = json.loads(out.read_text())
    assert frozenset(bible.keys()) == REQUIRED_BIBLE_KEYS
    assert bible["project_title"] == "CLI Direct Smoke"
    assert bible["genre"] == "Sci-Fi"
    assert "Production Bible ready" in result.stdout or "Next steps" in result.stdout


def test_create_bible_non_tty_without_title_fails() -> None:
    # Subprocess stdin is a pipe (not a TTY) when we don't allocate a pty.
    result = run_cli("create-bible")
    assert result.returncode == 2
    combined = result.stdout + result.stderr
    assert "title" in combined.lower() or "wizard" in combined.lower()


def test_create_bible_wizard_non_tty_fails() -> None:
    result = run_cli("create-bible", "--wizard")
    assert result.returncode == 2
    combined = result.stdout + result.stderr
    assert "interactive" in combined.lower() or "wizard" in combined.lower()


def test_run_bible_wizard_with_injected_input(tmp_path: Path) -> None:
    """Full wizard path without a real TTY — drives input_fn."""
    out = tmp_path / "wiz.json"
    # Stages: story (title, logline), genre (genre, director, complexity),
    # characters (chars, world), technicals (duration, video, chat, tech), review confirm
    responses = iter(
        [
            "Wizard Project",  # title
            "A short logline.",  # logline
            "",  # genre → default/seed
            "Moody grain",  # director
            "",  # complexity default
            "Hero: quiet lead",  # characters
            "Foggy pier",  # world
            "72",  # duration
            "",  # video default
            "",  # chat default
            "16:9",  # tech notes
            "y",  # confirm
        ]
    )

    def fake_input(_label: str) -> str:
        try:
            return next(responses)
        except StopIteration as exc:
            raise AssertionError("wizard asked for more input than expected") from exc

    saved: dict = {}

    def persist(bible: dict, output: str) -> None:
        Path(output).write_text(json.dumps(bible, indent=2))
        saved["bible"] = bible
        saved["output"] = output

    bible = run_bible_wizard(
        seed={"genre": "Thriller", "video_model": "1.0", "chat_model": "grok-4.3"},
        output=str(out),
        persist=persist,
        input_fn=fake_input,
    )
    assert saved["output"] == str(out)
    assert frozenset(bible.keys()) == REQUIRED_BIBLE_KEYS
    assert bible["project_title"] == "Wizard Project"
    assert bible["genre"] == "Thriller"
    assert bible["target_duration_seconds"] == 72
    assert "logline" in bible["notes"].lower() or "short logline" in bible["notes"].lower()
    assert "Hero" in bible["notes"]
    assert json.loads(out.read_text())["project_title"] == "Wizard Project"


def test_run_bible_wizard_quit(tmp_path: Path) -> None:
    import typer

    def fake_input(_label: str) -> str:
        return "q"

    with pytest.raises(typer.Exit) as ei:
        run_bible_wizard(
            seed={},
            output=str(tmp_path / "x.json"),
            persist=lambda b, o: None,
            input_fn=fake_input,
        )
    assert ei.value.exit_code == 1
