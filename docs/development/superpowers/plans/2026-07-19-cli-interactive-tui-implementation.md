# Interactive CLI Terminal UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `cinematic-studio ui` — a Textual TUI with a live studio dashboard (from `build_studio_dashboard()`) and a safe command launcher that runs existing CLI subcommands via subprocess.

**Architecture:** Thin Textual package under `tools/cli/tui/` owns layout, keys, and refresh only. Snapshot data comes exclusively from `cli.dashboard.build_studio_dashboard()`. Launcher catalog is static data; commands run as `sys.executable tools/cinematic_studio_cli.py <argv…>` with captured output on a separate screen.

**Tech Stack:** Python 3.12+, Typer, Rich (existing), Textual ≥ 0.47, pytest.

**Design:** [docs/development/superpowers/specs/2026-07-19-cli-interactive-tui-design.md](../specs/2026-07-19-cli-interactive-tui-design.md)

## Global Constraints

- Data for Home panels: **only** `build_studio_dashboard()` — no parallel aggregation.
- Launcher: **safe, non-interactive** argv only; never include `--wizard`, `run`, `submit`, spend commands.
- Subprocess timeout default: **60** seconds.
- Auto-refresh default: **5.0** seconds; minimum **1.0**.
- Non-TTY and missing Textual → exit code **1** with clear message; do not call `App.run()`.
- Existing `dashboard` / Streamlit / Typer commands **unchanged** in behavior.
- Tests must not require a full PTY Textual pilot run in CI.
- Repo root discovery: same pattern as tests (`Path(__file__).resolve().parents[…]`).

## File structure

| Path | Responsibility |
|------|----------------|
| `tools/cli/tui/__init__.py` | Export `run_tui` |
| `tools/cli/tui/catalog.py` | `LauncherEntry` + `LAUNCHER_CATALOG` |
| `tools/cli/tui/runner.py` | Resolve CLI path; `run_cli_command(argv, timeout=…)` |
| `tools/cli/tui/widgets.py` | `format_home_markdown(snapshot) -> str` (pure; no Textual import required) |
| `tools/cli/tui/screens.py` | Home, Launcher, CommandOutput, Help screens |
| `tools/cli/tui/app.py` | `StudioTUI` app + `run_tui(interval=5.0)` |
| `tools/cli/tui_commands.py` | Typer `ui` command registration |
| `tools/cinematic_studio_cli.py` | Register `tui_commands` |
| `requirements.txt` | Add `textual>=0.47.0` |
| `tests/test_tui_catalog.py` | Catalog safety |
| `tests/test_tui_runner.py` | Runner resolution + mocked subprocess |
| `tests/test_tui_widgets.py` | Snapshot → markdown |
| `tests/test_cli_smoke.py` | Extend: `ui --help` |
| `README.md` | One-liner for `cinematic-studio ui` |

---

### Task 1: Dependency + launcher catalog (TDD)

**Files:**
- Create: `tools/cli/tui/__init__.py`
- Create: `tools/cli/tui/catalog.py`
- Create: `tests/test_tui_catalog.py`
- Modify: `requirements.txt`

**Interfaces:**
- Consumes: nothing
- Produces:
  - `@dataclass(frozen=True) class LauncherEntry` with fields `id: str`, `label: str`, `description: str`, `argv: list[str]`
  - `LAUNCHER_CATALOG: tuple[LauncherEntry, ...]`
  - `FORBIDDEN_ARGV_TOKENS: frozenset[str]` = `{"--wizard", "run", "submit", "record", "cancel", "declutter"}` (safety net for tests)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_tui_catalog.py
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.tui.catalog import FORBIDDEN_ARGV_TOKENS, LAUNCHER_CATALOG  # noqa: E402


def test_catalog_non_empty() -> None:
    assert len(LAUNCHER_CATALOG) >= 8


def test_catalog_entries_have_stable_ids_and_argv() -> None:
    ids = [e.id for e in LAUNCHER_CATALOG]
    assert len(ids) == len(set(ids))
    for entry in LAUNCHER_CATALOG:
        assert entry.label.strip()
        assert entry.argv
        assert all(isinstance(a, str) and a for a in entry.argv)


def test_catalog_excludes_dangerous_tokens() -> None:
    for entry in LAUNCHER_CATALOG:
        for token in entry.argv:
            assert token not in FORBIDDEN_ARGV_TOKENS, f"{entry.id}: {token}"
        assert "--wizard" not in entry.argv


def test_catalog_includes_required_commands() -> None:
    argvs = {" ".join(e.argv) for e in LAUNCHER_CATALOG}
    for required in (
        "status",
        "dashboard --compact",
        "models list",
        "models verify",
        "quota dashboard",
        "dna list",
        "sequence list",
        "imagine list",
        "plugin list",
    ):
        assert required in argvs
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_tui_catalog.py -v`  
Expected: FAIL with `ModuleNotFoundError` or import error for `cli.tui.catalog`

- [ ] **Step 3: Add dependency and implement catalog**

Append to `requirements.txt`:

```
textual>=0.47.0
```

```python
# tools/cli/tui/__init__.py
"""Interactive Textual TUI for cinematic-studio."""

from __future__ import annotations

__all__ = ["run_tui"]


def __getattr__(name: str):
    if name == "run_tui":
        from cli.tui.app import run_tui

        return run_tui
    raise AttributeError(name)
```

```python
# tools/cli/tui/catalog.py
"""Safe launcher catalog for the studio TUI (static; no Typer scraping)."""

from __future__ import annotations

from dataclasses import dataclass


FORBIDDEN_ARGV_TOKENS: frozenset[str] = frozenset(
    {
        "--wizard",
        "run",
        "submit",
        "record",
        "cancel",
        "declutter",
    }
)


@dataclass(frozen=True)
class LauncherEntry:
    id: str
    label: str
    description: str
    argv: list[str]


LAUNCHER_CATALOG: tuple[LauncherEntry, ...] = (
    LauncherEntry("status", "Studio status", "Version, agents, activation", ["status"]),
    LauncherEntry(
        "dashboard_compact",
        "Dashboard (compact)",
        "Summary panels only",
        ["dashboard", "--compact"],
    ),
    LauncherEntry("models_list", "Models list", "Registered model stack", ["models", "list"]),
    LauncherEntry("models_verify", "Models verify", "Compatibility check", ["models", "verify"]),
    LauncherEntry(
        "quota_dashboard",
        "Quota dashboard",
        "Session spend and budget",
        ["quota", "dashboard"],
    ),
    LauncherEntry("dna_list", "DNA list", "Character DNA profiles", ["dna", "list"]),
    LauncherEntry(
        "sequence_list",
        "Sequences list",
        "Long-form sequences",
        ["sequence", "list"],
    ),
    LauncherEntry("imagine_list", "Imagine jobs", "Recent Imagine jobs", ["imagine", "list"]),
    LauncherEntry("plugin_list", "Plugin list", "Installed plugin skills", ["plugin", "list"]),
)
```

- [ ] **Step 4: Install textual and run tests**

Run:

```bash
pip install 'textual>=0.47.0'
pytest tests/test_tui_catalog.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add requirements.txt tools/cli/tui/__init__.py tools/cli/tui/catalog.py tests/test_tui_catalog.py
git commit -m "feat(tui): add launcher catalog and textual dependency"
```

---

### Task 2: CLI subprocess runner (TDD)

**Files:**
- Create: `tools/cli/tui/runner.py`
- Create: `tests/test_tui_runner.py`

**Interfaces:**
- Consumes: none
- Produces:
  - `repo_root() -> Path`
  - `cli_script_path() -> Path` → `<repo>/tools/cinematic_studio_cli.py`
  - `run_cli_command(argv: list[str], *, timeout: float = 60.0, cwd: Path | None = None) -> CommandResult`
  - `@dataclass class CommandResult` with `argv: list[str]`, `returncode: int`, `stdout: str`, `stderr: str`, `timed_out: bool`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_tui_runner.py
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.tui.runner import (  # noqa: E402
    cli_script_path,
    repo_root,
    run_cli_command,
)


def test_repo_root_and_cli_script_exist() -> None:
    root = repo_root()
    assert (root / "VERSION").is_file()
    script = cli_script_path()
    assert script.is_file()
    assert script.name == "cinematic_studio_cli.py"


def test_run_cli_command_status_succeeds() -> None:
    result = run_cli_command(["status"], timeout=30.0)
    assert result.timed_out is False
    assert result.returncode == 0
    assert result.stdout
    assert "Grok" in result.stdout or "4.5" in result.stdout or "Studio" in result.stdout


def test_run_cli_command_timeout_sets_flag() -> None:
    fake = MagicMock()
    with patch("cli.tui.runner.subprocess.run", side_effect=TimeoutError("x")):
        # Implementation should catch subprocess.TimeoutExpired — patch that path
        pass
```

Prefer implementing timeout via `subprocess.TimeoutExpired`:

```python
def test_run_cli_command_timeout_sets_flag() -> None:
    import subprocess as sp

    with patch(
        "cli.tui.runner.subprocess.run",
        side_effect=sp.TimeoutExpired(cmd=["x"], timeout=0.01),
    ):
        result = run_cli_command(["status"], timeout=0.01)
    assert result.timed_out is True
    assert result.returncode != 0
    assert "timed out" in result.stderr.lower() or "timed out" in result.stdout.lower()
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `pytest tests/test_tui_runner.py -v`  
Expected: FAIL import / missing module

- [ ] **Step 3: Implement runner**

```python
# tools/cli/tui/runner.py
"""Subprocess runner for safe CLI commands from the TUI."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandResult:
    argv: list[str]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


def repo_root() -> Path:
    # tools/cli/tui/runner.py → parents[0]=tui, [1]=cli, [2]=tools, [3]=repo
    return Path(__file__).resolve().parents[3]


def cli_script_path() -> Path:
    return repo_root() / "tools" / "cinematic_studio_cli.py"


def run_cli_command(
    argv: list[str],
    *,
    timeout: float = 60.0,
    cwd: Path | None = None,
) -> CommandResult:
    if not argv:
        return CommandResult(
            argv=[],
            returncode=2,
            stdout="",
            stderr="No command argv provided.",
            timed_out=False,
        )
    script = cli_script_path()
    cmd = [sys.executable, str(script), *argv]
    workdir = cwd or repo_root()
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(workdir),
            timeout=max(1.0, float(timeout)),
        )
        return CommandResult(
            argv=list(argv),
            returncode=int(completed.returncode),
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        err = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        msg = f"Command timed out after {timeout}s: {' '.join(argv)}"
        return CommandResult(
            argv=list(argv),
            returncode=124,
            stdout=out,
            stderr=(err + "\n" + msg).strip(),
            timed_out=True,
        )
```

- [ ] **Step 4: Run tests — expect PASS**

Run: `pytest tests/test_tui_runner.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/cli/tui/runner.py tests/test_tui_runner.py
git commit -m "feat(tui): add CLI subprocess runner for launcher"
```

---

### Task 3: Home snapshot → markdown formatter (TDD)

**Files:**
- Create: `tools/cli/tui/widgets.py`
- Create: `tests/test_tui_widgets.py`

**Interfaces:**
- Consumes: snapshot `dict` shape from `build_studio_dashboard()`
- Produces: `format_home_markdown(snapshot: dict) -> str` — plain markdown/text for Textual `Static` / `Markdown`
- Produces: `format_error_panel(message: str) -> str`

Keep pure Python (no Textual import) so tests stay light.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_tui_widgets.py
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.dashboard import build_studio_dashboard  # noqa: E402
from cli.tui.widgets import format_error_panel, format_home_markdown  # noqa: E402


def test_format_home_markdown_from_live_snapshot() -> None:
    snap = build_studio_dashboard()
    text = format_home_markdown(snap)
    assert "Studio" in text or snap["studio_version"] in text
    assert snap["project"]["title"] in text or "Project" in text
    assert "Quota" in text or "quota" in text.lower()
    assert "Models" in text or "compatible" in text.lower() or "issues" in text.lower()


def test_format_error_panel() -> None:
    text = format_error_panel("boom")
    assert "boom" in text
    assert "Error" in text or "error" in text.lower()
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_tui_widgets.py -v`  
Expected: FAIL import

- [ ] **Step 3: Implement widgets**

```python
# tools/cli/tui/widgets.py
"""Pure formatters: dashboard snapshot → text for Textual widgets."""

from __future__ import annotations

from typing import Any


def format_error_panel(message: str) -> str:
    return f"## Error\n\n{message}\n\nPress **r** to retry · **q** to quit."


def format_home_markdown(snapshot: dict[str, Any]) -> str:
    project = snapshot.get("project") or {}
    studio = snapshot.get("studio") or {}
    quota = snapshot.get("quota") or {}
    production = snapshot.get("production") or {}
    stack = studio.get("model_stack") or {}

    title = project.get("title") or "Untitled"
    genre = project.get("genre") or "—"
    models = "compatible" if studio.get("models_compatible") else "ISSUES"
    remaining = quota.get("budget_remaining")
    remaining_s = f"{remaining} credits" if remaining is not None else "—"

    lines = [
        f"# Grok Imagine Cinematic Studio v{snapshot.get('studio_version', '?')}",
        f"_{snapshot.get('generated_at', '')}_",
        "",
        f"**Project:** {title}  ",
        f"**Genre:** {genre}  ",
        f"**Bible:** {'loaded' if project.get('has_bible') else 'not started'}",
        "",
        "## Studio Health",
        f"- Agents: {studio.get('core_agents', '?')} core · {studio.get('total_agents', '?')} total",
        f"- Role cards: {studio.get('role_cards', '?')}/{studio.get('role_cards_expected', '?')}",
        f"- Skills: {studio.get('skills', '?')}",
        f"- Models: **{models}**",
        f"- Chat: `{stack.get('xai_chat', '—')}` · Video: `{stack.get('imagine_video', '—')}`",
        "",
        "## Quota",
        f"- Tier: {quota.get('tier_label', quota.get('tier', '—'))}",
        f"- Session spent: {quota.get('session_spent', 0)} credits",
        f"- Budget left: {remaining_s}",
        f"- Risk: **{quota.get('risk_level', 'unknown')}**",
        "",
        "## Production",
        f"- Sequences: {production.get('sequences', 0)}",
        f"- DNA profiles: {production.get('characters', 0)} "
        f"(locked: {production.get('identity_locked', 0)})",
        f"- Imagine jobs: {production.get('imagine_jobs', 0)}",
        f"- SFW / NSFW batches: {production.get('sfw_batches', 0)} / "
        f"{production.get('nsfw_batches', 0)}",
        "",
        "_Keys: **r** refresh · **l** launcher · **?** help · **q** quit_",
    ]

    # Compact sequence / character lines
    seqs = snapshot.get("sequences") or []
    if seqs:
        lines.append("")
        lines.append("## Sequences")
        for s in seqs[:6]:
            lines.append(
                f"- {s.get('name', '?')} · {s.get('clips', 0)} clips · "
                f"QA {s.get('chain_qa_status', 'pending')}"
            )

    chars = snapshot.get("characters") or []
    if chars:
        lines.append("")
        lines.append("## Characters")
        for c in chars[:6]:
            lines.append(f"- {c.get('name', '?')} (`{c.get('slug', '')}`) · {c.get('status', 'pending')}")

    return "\n".join(lines)
```

- [ ] **Step 4: Run — expect PASS**

Run: `pytest tests/test_tui_widgets.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/cli/tui/widgets.py tests/test_tui_widgets.py
git commit -m "feat(tui): format home dashboard markdown from snapshot"
```

---

### Task 4: Textual app + screens

**Files:**
- Create: `tools/cli/tui/screens.py`
- Create: `tools/cli/tui/app.py`
- Modify: `tools/cli/tui/__init__.py` (already lazy-exports `run_tui`)

**Interfaces:**
- Consumes: `build_studio_dashboard`, `format_home_markdown`, `format_error_panel`, `LAUNCHER_CATALOG`, `run_cli_command`
- Produces: `run_tui(*, interval: float = 5.0) -> None` — starts Textual app (blocking)
- Produces: class `StudioTUI(App[None])`

**Note:** Screens use Textual APIs. Pin patterns that work on Textual ≥ 0.47:

- `App` with `CSS` or `DEFAULT_CSS`
- `ComposeResult`, `Static`, `ListView`/`ListItem` or `OptionList`, `Footer`, `Header`
- Bindings: `r`, `l`, `q`, `question_mark`, `escape`, `h`

- [ ] **Step 1: Implement screens**

```python
# tools/cli/tui/screens.py
"""Textual screens for studio TUI."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Markdown, Static

from cli.tui.catalog import LAUNCHER_CATALOG, LauncherEntry
from cli.tui.runner import CommandResult, run_cli_command
from cli.tui.widgets import format_error_panel, format_home_markdown


class HomeScreen(Screen[None]):
    """Live dashboard home."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("l", "launcher", "Launcher"),
        Binding("q", "quit_app", "Quit"),
        Binding("question_mark", "help", "Help"),
        Binding("h", "home", "Home"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with VerticalScroll(id="home-scroll"):
            yield Markdown("", id="home-body")
        yield Footer()

    def on_mount(self) -> None:
        self.action_refresh()

    def action_refresh(self) -> None:
        body = self.query_one("#home-body", Markdown)
        try:
            from cli.dashboard import build_studio_dashboard

            snap = build_studio_dashboard()
            body.update(format_home_markdown(snap))
        except Exception as exc:  # noqa: BLE001 — surface any snapshot failure
            body.update(format_error_panel(str(exc)))

    def action_launcher(self) -> None:
        self.app.push_screen(LauncherScreen())

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())

    def action_home(self) -> None:
        pass  # already home

    def action_quit_app(self) -> None:
        self.app.exit()


class LauncherScreen(Screen[None]):
    """Pick a safe CLI command."""

    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("h", "close", "Home"),
        Binding("q", "quit_app", "Quit"),
        Binding("question_mark", "help", "Help"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Launcher — Enter to run · Esc back", id="launcher-hint")
        yield ListView(
            *[
                ListItem(
                    Label(f"{e.label}  [dim]{' '.join(e.argv)}[/dim]"),
                    id=f"entry-{e.id}",
                )
                for e in LAUNCHER_CATALOG
            ],
            id="launcher-list",
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        entry_id = item_id.removeprefix("entry-")
        entry = next((e for e in LAUNCHER_CATALOG if e.id == entry_id), None)
        if entry is None:
            return
        self._run_entry(entry)

    def _run_entry(self, entry: LauncherEntry) -> None:
        result = run_cli_command(list(entry.argv))
        self.app.push_screen(CommandOutputScreen(entry=entry, result=result))

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())

    def action_quit_app(self) -> None:
        self.app.exit()


class CommandOutputScreen(Screen[None]):
    """Show captured CLI output."""

    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, entry: LauncherEntry, result: CommandResult) -> None:
        super().__init__()
        self.entry = entry
        self.result = result

    def compose(self) -> ComposeResult:
        yield Header()
        code = self.result.returncode
        status = "OK" if code == 0 and not self.result.timed_out else f"FAIL ({code})"
        title = f"{self.entry.label} · {status} · `{' '.join(self.entry.argv)}`"
        body = self.result.stdout
        if self.result.stderr:
            body = (body + "\n\n--- stderr ---\n" + self.result.stderr).strip()
        if not body:
            body = "(no output)"
        with VerticalScroll():
            yield Static(title, id="out-title")
            yield Static(body, id="out-body")
        yield Footer()

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()


class HelpScreen(ModalScreen[None]):
    """Keybinding help."""

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Static(
                "\n".join(
                    [
                        "Studio TUI Help",
                        "",
                        "r  Refresh dashboard",
                        "l  Open launcher",
                        "h  Home / back",
                        "Esc  Back",
                        "?  This help",
                        "q  Quit",
                        "",
                        "Launcher runs safe read-only CLI commands only.",
                        "Wizards and spend flows stay on the classic CLI.",
                    ]
                ),
                id="help-body",
            ),
            id="help-dialog",
        )

    def action_close(self) -> None:
        self.app.pop_screen()
```

**ListView note:** If `ListView.Selected` / item `id` is awkward on the installed Textual version, use `OptionList` with `Option(prompt, id=entry.id)` and `on_option_list_option_selected` instead — keep the same catalog and runner calls.

- [ ] **Step 2: Implement app**

```python
# tools/cli/tui/app.py
"""Textual application entry for cinematic-studio ui."""

from __future__ import annotations

from textual.app import App

from cli.tui.screens import HomeScreen


class StudioTUI(App[None]):
    """Grok Imagine Cinematic Studio terminal UI."""

    TITLE = "Cinematic Studio"
    SUB_TITLE = "Dashboard + Launcher"
    CSS = """
    #home-scroll { height: 1fr; }
    #launcher-hint { padding: 1 2; color: $text-muted; }
    #out-title { padding: 1 2; text-style: bold; }
    #out-body { padding: 0 2 1 2; }
    #help-dialog {
        width: 60;
        height: auto;
        border: heavy $accent;
        background: $surface;
        padding: 1 2;
        align: center middle;
    }
    HelpScreen { align: center middle; }
    """

    def __init__(self, interval: float = 5.0) -> None:
        super().__init__()
        self.refresh_interval = max(1.0, float(interval))

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())
        self.set_interval(self.refresh_interval, self._auto_refresh)

    def _auto_refresh(self) -> None:
        screen = self.screen
        if isinstance(screen, HomeScreen):
            screen.action_refresh()


def run_tui(*, interval: float = 5.0) -> None:
    """Run the studio TUI (blocking). Caller must ensure TTY + Textual installed."""
    StudioTUI(interval=interval).run()
```

- [ ] **Step 3: Smoke-import test (no App.run)**

Add to `tests/test_tui_widgets.py` or new `tests/test_tui_app_import.py`:

```python
def test_studio_tui_importable() -> None:
    from cli.tui.app import StudioTUI, run_tui

    assert callable(run_tui)
    app = StudioTUI(interval=5.0)
    assert app.refresh_interval == 5.0
```

Run: `pytest tests/test_tui_widgets.py tests/test_tui_catalog.py tests/test_tui_runner.py -v`  
Expected: PASS (after adding import test)

- [ ] **Step 4: Manual sanity (optional on TTY)**

```bash
python tools/cinematic_studio_cli.py ui
# expect Home; press l, Enter on status, Esc, q
```

- [ ] **Step 5: Commit**

```bash
git add tools/cli/tui/app.py tools/cli/tui/screens.py tests/
git commit -m "feat(tui): Textual StudioTUI home, launcher, and output screens"
```

---

### Task 5: Typer `ui` command + guards

**Files:**
- Create: `tools/cli/tui_commands.py`
- Modify: `tools/cinematic_studio_cli.py` — import and `register_tui_commands(app)`
- Modify: `tests/test_cli_smoke.py` — assert `ui` in help and `ui --help` works

**Interfaces:**
- Consumes: `run_tui`
- Produces: `register(app: typer.Typer) -> None` with command `ui`

- [ ] **Step 1: Extend smoke test (fail first for help text if ui missing)**

```python
# add to tests/test_cli_smoke.py

def test_ui_help() -> None:
    result = run_cli("ui", "--help")
    assert result.returncode == 0, result.stderr
    assert "interactive" in result.stdout.lower() or "tui" in result.stdout.lower() or "terminal" in result.stdout.lower()


def test_main_help_lists_ui() -> None:
    result = run_cli("--help")
    assert result.returncode == 0
    assert "ui" in result.stdout
```

Also update `test_main_help` optionally to include `"ui"`.

- [ ] **Step 2: Run — expect FAIL** (ui unknown)

Run: `pytest tests/test_cli_smoke.py::test_ui_help -v`  
Expected: FAIL (no such command)

- [ ] **Step 3: Implement registration**

```python
# tools/cli/tui_commands.py
"""Register cinematic-studio ui (Textual TUI)."""

from __future__ import annotations

import sys

import typer

from cli.shared import console


def register(app: typer.Typer) -> None:
    @app.command("ui")
    def ui(
        interval: float = typer.Option(
            5.0,
            "--interval",
            "-i",
            help="Home auto-refresh seconds (min 1.0)",
            min=1.0,
        ),
    ) -> None:
        """Interactive terminal UI — live studio dashboard + command launcher."""
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            console.print(
                "[red]cinematic-studio ui requires an interactive terminal.[/red]"
            )
            raise typer.Exit(1)
        try:
            import textual  # noqa: F401
        except ImportError as exc:
            console.print(
                "[red]Textual is required for the TUI.[/red]\n"
                "Install with: [bold]pip install 'textual>=0.47.0'[/bold] "
                "(or pip install -r requirements.txt)"
            )
            raise typer.Exit(1) from exc

        from cli.tui.app import run_tui

        run_tui(interval=interval)
```

Wire in `tools/cinematic_studio_cli.py`:

```python
from cli.tui_commands import register as register_tui_commands  # noqa: E402
# after other registers:
register_tui_commands(app)
```

- [ ] **Step 4: Run smoke tests**

```bash
pytest tests/test_cli_smoke.py -v
# Also: python tools/cinematic_studio_cli.py ui </dev/null
# expect exit 1 and "interactive terminal"
```

Expected: smoke PASS; non-TTY exit 1

- [ ] **Step 5: Commit**

```bash
git add tools/cli/tui_commands.py tools/cinematic_studio_cli.py tests/test_cli_smoke.py
git commit -m "feat(cli): register cinematic-studio ui with TTY and Textual guards"
```

---

### Task 6: README note + full verification

**Files:**
- Modify: `README.md` — near CLI / dashboard section, add:

```markdown
# Interactive terminal UI (dashboard + safe command launcher)
cinematic-studio ui
# or: python tools/cinematic_studio_cli.py ui --interval 5
```

Optional one line under Web UI contrasting Streamlit vs TUI.

- [ ] **Step 1: Edit README** near existing CLI examples (search for `dashboard` or `create-bible`)

- [ ] **Step 2: Run full related suite**

```bash
pytest tests/test_tui_catalog.py tests/test_tui_runner.py tests/test_tui_widgets.py tests/test_cli_smoke.py tests/test_cli_dashboard.py -v
```

Expected: all PASS

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: document cinematic-studio ui terminal TUI"
```

---

## Spec coverage checklist

| Spec requirement | Task |
|------------------|------|
| `cinematic-studio ui` entry | Task 5 |
| Home live dashboard from `build_studio_dashboard` | Tasks 3–4 |
| Auto-refresh 5s + `--interval` | Tasks 4–5 |
| Launcher safe catalog | Task 1 |
| Subprocess runner + output screen | Tasks 2, 4 |
| Keys r/l/q/?/Esc/h | Task 4 |
| Non-TTY + missing Textual exit 1 | Task 5 |
| Tests without PTY E2E | Tasks 1–3, 5 |
| `textual` in requirements | Task 1 |
| README one-liner | Task 6 |
| Streamlit / dashboard unchanged | All (no edits to those paths) |

## Out of scope (do not implement in this plan)

- Bible wizard, NSFW run, imagine submit in launcher
- Streamlit changes
- VERSION bump / CHANGELOG (optional follow-up release note)
- PTY attach for interactive subcommands

## Self-review notes

- No TBD placeholders; interfaces named consistently (`run_tui`, `CommandResult`, `LauncherEntry`, `format_home_markdown`).
- `ListView` vs `OptionList`: screens task allows OptionList fallback if Textual version differs.
- Lazy `run_tui` import in `__init__` avoids hard Textual import for catalog-only tests.
