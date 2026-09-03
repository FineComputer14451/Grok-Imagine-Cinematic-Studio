"""Tests for React/TanStack cockpit packaging + CLI entry."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_web_react_package_layout() -> None:
    app = ROOT / "web_react"
    assert (app / "package.json").is_file()
    assert (app / "vite.config.ts").is_file()
    assert (app / "src" / "main.tsx").is_file()
    assert (app / "src" / "router.tsx").is_file()
    assert (app / "src" / "api" / "client.ts").is_file()
    assert (app / "src" / "components" / "ToolsView.tsx").is_file()
    assert (app / "src" / "components" / "SettingsView.tsx").is_file()
    assert (app / "src" / "components" / "NsfwView.tsx").is_file()
    settings = (app / "src" / "components" / "SettingsView.tsx").read_text(encoding="utf-8")
    assert "I am 18 or older" in settings
    assert "imaginary adults" in settings
    assert "nsfw attest" in settings
    assert "canEnableNsfwNav" in (app / "src" / "lib" / "settingsPrefs.ts").read_text(
        encoding="utf-8"
    )
    assert (app / "README.md").is_file()


def test_web_react_phase2_routes_in_router() -> None:
    text = (ROOT / "web_react" / "src" / "router.tsx").read_text(encoding="utf-8")
    for path in ("/tools", "/settings", "/nsfw", "/production", "/quota", "/bible"):
        assert path in text
    assert "GuidedBibleView" in text


def test_web_react_e2e_assets_present() -> None:
    app = ROOT / "web_react"
    assert (app / "e2e" / "http-smoke.mjs").is_file()
    assert (app / "e2e" / "smoke-routes.spec.ts").is_file()
    assert (app / "e2e" / "start-stack.sh").is_file()
    assert (app / "playwright.config.ts").is_file()
    pkg = (app / "package.json").read_text(encoding="utf-8")
    assert "test:smoke" in pkg
    assert "test:e2e" in pkg


def test_web_react_prefs_map_covers_bible_fields() -> None:
    text = (ROOT / "web_react" / "src" / "lib" / "prefsToAnswers.ts").read_text(
        encoding="utf-8"
    )
    for key in ("genre", "chat_model", "video_model", "duration", "tier"):
        assert f"{key}:" in text or f"'{key}'" in text or f'"{key}"' in text
    assert "applyPrefsToFieldDefaults" in text


def test_web_react_package_json_scripts() -> None:
    import json

    pkg = json.loads((ROOT / "web_react" / "package.json").read_text(encoding="utf-8"))
    scripts = pkg.get("scripts") or {}
    assert "dev" in scripts
    assert "build" in scripts
    assert "preview" in scripts
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    for name in (
        "@tanstack/react-query",
        "@tanstack/react-router",
        "@tanstack/react-form",
        "@tanstack/react-table",
        "react",
        "vite",
    ):
        assert name in deps, f"missing dep {name}"


def test_web_react_command_help() -> None:
    from cli_helpers import run_cli

    result = run_cli("web-react", "--help")
    assert result.returncode == 0, result.stderr
    out = result.stdout.lower()
    assert "react" in out or "tanstack" in out or "web-react" in out
    assert "--port" in result.stdout
    assert "--api-url" in result.stdout or "api-url" in out


def test_main_help_lists_web_react() -> None:
    from cli_helpers import run_cli

    result = run_cli("--help")
    assert result.returncode == 0
    assert "web-react" in result.stdout


def test_web_react_dir_helper() -> None:
    """Command module resolves path under repo root (sanity)."""
    import sys

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    from cli.web_react_commands import _web_react_dir

    d = _web_react_dir()
    assert d.name == "web_react"
    assert d.is_dir()
    assert (d / "package.json").is_file()


if __name__ == "__main__":
    test_web_react_package_layout()
    test_web_react_package_json_scripts()
    test_web_react_command_help()
    test_main_help_lists_web_react()
    test_web_react_dir_helper()
    print("web_react tests passed")
