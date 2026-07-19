# CLI TUI Full Cockpit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `cinematic-studio ui` with a production Cockpit (`c`): form → confirm → CLI for Bible, DNA init, sequence init, and quota budget, plus immediate models verify — without generation spend or `--wizard`.

**Architecture:** Pure `tools/cli/tui/forms.py` mappers (`validate_answers` / `answers_to_argv` / `summarize_action`) drive Textual Form + Confirm screens. Execution reuses `run_cli_command` and `CommandOutputScreen`. Home gains binding `c` → Cockpit menu.

**Tech Stack:** Python 3.12+, Textual (existing), Typer CLI (subprocess), pytest.

**Design:** [docs/development/superpowers/specs/2026-07-19-cli-tui-full-cockpit-design.md](../specs/2026-07-19-cli-tui-full-cockpit-design.md)

## Global Constraints

- Thin TUI only — no second Bible/DNA schema; CLI owns writes.
- Bible path: non-interactive `create-bible` only — **never** `--wizard`.
- Forbidden in any cockpit argv: `--wizard`, `run`, `submit`, `record`, `cancel`, `declutter`.
- Execute via `run_cli_command` (default timeout 60s) + Command Output screen.
- Valid quota tiers: `supergrok_pro`, `supergrok_heavy`, `custom`.
- Mutating workflows: Form → Confirm → CLI. `models_verify`: immediate run, no form.
- No PTY E2E required in CI; pure form tests without `App.run()`.
- v1 launcher catalog and dashboard behavior unchanged.
- Streamlit unchanged.

## File structure

| Path | Responsibility |
|------|----------------|
| `tools/cli/tui/forms.py` | `FormField`, `WorkflowSpec`, `COCKPIT_WORKFLOWS`, validate/argv/summarize |
| `tools/cli/tui/screens.py` | + CockpitMenu, Form, Confirm; Home `c`; Help text; flexible CommandOutput label |
| `tools/cli/tui/app.py` | SUB_TITLE + CSS for form/confirm |
| `tools/cli/tui/widgets.py` | Optional `format_form_errors(errors: list[str]) -> str` |
| `tests/test_tui_forms.py` | Pure mapper tests |
| `README.md` | Cockpit one-liner under `ui` |

---

### Task 1: Pure forms module (TDD)

**Files:**
- Create: `tools/cli/tui/forms.py`
- Create: `tests/test_tui_forms.py`

**Interfaces:**
- Consumes: nothing from Textual; optional hardcode tier set (do not import heavy quota at import-time if avoidable — hardcode the three tier ids from the design)
- Produces:
  - `@dataclass(frozen=True) class FormField` with `key`, `label`, `required: bool = False`, `default: str = ""`, `help: str = ""`
  - `@dataclass(frozen=True) class WorkflowSpec` with `id`, `label`, `description`, `fields: tuple[FormField, ...]`, `needs_confirm: bool = True`
  - `COCKPIT_WORKFLOWS: dict[str, WorkflowSpec]` with keys: `bible_create`, `dna_init`, `sequence_init`, `quota_budget`, `models_verify`
  - `COCKPIT_ORDER: tuple[str, ...]` = ordered ids for the menu
  - `VALID_QUOTA_TIERS: frozenset[str]` = `{"supergrok_pro", "supergrok_heavy", "custom"}`
  - `validate_answers(workflow_id: str, answers: dict[str, str]) -> list[str]`
  - `answers_to_argv(workflow_id: str, answers: dict[str, str]) -> list[str]`
  - `summarize_action(workflow_id: str, answers: dict[str, str]) -> str`
  - `default_answers(workflow_id: str) -> dict[str, str]` — field defaults for form prefill

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_tui_forms.py
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.tui.catalog import FORBIDDEN_ARGV_TOKENS  # noqa: E402
from cli.tui.forms import (  # noqa: E402
    COCKPIT_ORDER,
    COCKPIT_WORKFLOWS,
    answers_to_argv,
    default_answers,
    summarize_action,
    validate_answers,
)


def test_cockpit_order_and_ids() -> None:
    assert COCKPIT_ORDER == (
        "bible_create",
        "dna_init",
        "sequence_init",
        "quota_budget",
        "models_verify",
    )
    assert set(COCKPIT_WORKFLOWS) == set(COCKPIT_ORDER)
    assert COCKPIT_WORKFLOWS["models_verify"].fields == ()
    assert COCKPIT_WORKFLOWS["models_verify"].needs_confirm is False
    for wid in ("bible_create", "dna_init", "sequence_init", "quota_budget"):
        assert COCKPIT_WORKFLOWS[wid].needs_confirm is True
        assert COCKPIT_WORKFLOWS[wid].fields


def test_bible_happy_argv() -> None:
    answers = {
        "title": "Neon Echo",
        "genre": "Sci-Fi",
        "chat_model": "grok-4.5",
        "video_model": "grok-imagine-video",
        "output": "production_bible.json",
    }
    assert validate_answers("bible_create", answers) == []
    argv = answers_to_argv("bible_create", answers)
    assert argv == [
        "create-bible",
        "Neon Echo",
        "--genre",
        "Sci-Fi",
        "--chat-model",
        "grok-4.5",
        "--video-model",
        "grok-imagine-video",
        "-o",
        "production_bible.json",
    ]
    assert "--wizard" not in argv


def test_bible_missing_title() -> None:
    errs = validate_answers("bible_create", default_answers("bible_create"))
    assert any("title" in e.lower() for e in errs)


def test_dna_optional_flags_omitted_when_empty() -> None:
    answers = {"name": "Liora", "core": "", "facial": "soft", "hair": "", "clothing": "", "emotion": ""}
    assert validate_answers("dna_init", answers) == []
    argv = answers_to_argv("dna_init", answers)
    assert argv[:3] == ["dna", "init", "Liora"]
    assert "--facial" in argv and "soft" in argv
    assert "--core" not in argv
    assert "--hair" not in argv


def test_sequence_duration_and_genre() -> None:
    assert validate_answers("sequence_init", {"name": "Act 1", "duration": "90", "genre": "Drama"}) == []
    argv = answers_to_argv("sequence_init", {"name": "Act 1", "duration": "90", "genre": "Drama"})
    assert argv == ["sequence", "init", "Act 1", "-d", "90", "-g", "Drama"]
    assert validate_answers("sequence_init", {"name": "X", "duration": "0", "genre": ""})
    assert validate_answers("sequence_init", {"name": "X", "duration": "nope", "genre": ""})


def test_quota_budget_tier_and_remaining() -> None:
    assert validate_answers("quota_budget", {"tier": "supergrok_pro", "remaining": ""}) == []
    assert answers_to_argv("quota_budget", {"tier": "supergrok_pro", "remaining": ""}) == [
        "quota",
        "budget",
        "--tier",
        "supergrok_pro",
    ]
    argv = answers_to_argv("quota_budget", {"tier": "supergrok_heavy", "remaining": "500"})
    assert argv == ["quota", "budget", "--tier", "supergrok_heavy", "--remaining", "500"]
    assert validate_answers("quota_budget", {"tier": "free_tier", "remaining": ""})


def test_models_verify_argv() -> None:
    assert validate_answers("models_verify", {}) == []
    assert answers_to_argv("models_verify", {}) == ["models", "verify"]


def test_no_forbidden_tokens_in_any_happy_path() -> None:
    samples = {
        "bible_create": {
            "title": "T",
            "genre": "Cinematic",
            "chat_model": "grok-4.5",
            "video_model": "grok-imagine-video",
            "output": "production_bible.json",
        },
        "dna_init": {
            "name": "N",
            "core": "c",
            "facial": "",
            "hair": "",
            "clothing": "",
            "emotion": "",
        },
        "sequence_init": {"name": "S", "duration": "60", "genre": ""},
        "quota_budget": {"tier": "custom", "remaining": "1"},
        "models_verify": {},
    }
    for wid, ans in samples.items():
        assert validate_answers(wid, ans) == []
        argv = answers_to_argv(wid, ans)
        for tok in FORBIDDEN_ARGV_TOKENS:
            assert tok not in argv, f"{wid}: forbidden {tok}"
        assert "--wizard" not in argv


def test_summarize_includes_label_and_argv() -> None:
    text = summarize_action(
        "bible_create",
        {
            "title": "Neon",
            "genre": "Cinematic",
            "chat_model": "grok-4.5",
            "video_model": "grok-imagine-video",
            "output": "production_bible.json",
        },
    )
    assert "Bible" in text or "bible" in text.lower() or "Neon" in text
    assert "create-bible" in text


def test_unknown_workflow() -> None:
    errs = validate_answers("nope", {})
    assert errs
    try:
        answers_to_argv("nope", {})
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `pytest tests/test_tui_forms.py -v`  
Expected: FAIL `ModuleNotFoundError` for `cli.tui.forms`

- [ ] **Step 3: Implement `forms.py`**

```python
# tools/cli/tui/forms.py
"""Pure cockpit workflow specs: form fields → CLI argv (no Textual)."""

from __future__ import annotations

from dataclasses import dataclass


VALID_QUOTA_TIERS: frozenset[str] = frozenset(
    {"supergrok_pro", "supergrok_heavy", "custom"}
)


@dataclass(frozen=True)
class FormField:
    key: str
    label: str
    required: bool = False
    default: str = ""
    help: str = ""


@dataclass(frozen=True)
class WorkflowSpec:
    id: str
    label: str
    description: str
    fields: tuple[FormField, ...]
    needs_confirm: bool = True


COCKPIT_WORKFLOWS: dict[str, WorkflowSpec] = {
    "bible_create": WorkflowSpec(
        id="bible_create",
        label="Create Production Bible",
        description="Non-interactive create-bible (no wizard)",
        fields=(
            FormField("title", "Project title", required=True),
            FormField("genre", "Genre", default="Cinematic"),
            FormField("chat_model", "Chat model", default="grok-4.5"),
            FormField("video_model", "Video model", default="grok-imagine-video"),
            FormField("output", "Output path", default="production_bible.json"),
        ),
        needs_confirm=True,
    ),
    "dna_init": WorkflowSpec(
        id="dna_init",
        label="Init Character DNA",
        description="Scaffold a Character DNA profile",
        fields=(
            FormField("name", "Character name", required=True),
            FormField("core", "Core identity", help="--core"),
            FormField("facial", "Facial DNA", help="--facial"),
            FormField("hair", "Hair & grooming", help="--hair"),
            FormField("clothing", "Clothing & style", help="--clothing"),
            FormField("emotion", "Emotional baseline", help="--emotion"),
        ),
        needs_confirm=True,
    ),
    "sequence_init": WorkflowSpec(
        id="sequence_init",
        label="Init Sequence",
        description="Create a long-form sequence blueprint",
        fields=(
            FormField("name", "Sequence name", required=True),
            FormField("duration", "Target duration (seconds)", default="60"),
            FormField("genre", "Genre"),
        ),
        needs_confirm=True,
    ),
    "quota_budget": WorkflowSpec(
        id="quota_budget",
        label="Set Quota Budget",
        description="Set subscription tier and remaining credits",
        fields=(
            FormField(
                "tier",
                "Tier (supergrok_pro|supergrok_heavy|custom)",
                required=True,
                default="supergrok_pro",
            ),
            FormField("remaining", "Remaining credits (optional)"),
        ),
        needs_confirm=True,
    ),
    "models_verify": WorkflowSpec(
        id="models_verify",
        label="Models Verify",
        description="Check model stack compatibility",
        fields=(),
        needs_confirm=False,
    ),
}

COCKPIT_ORDER: tuple[str, ...] = (
    "bible_create",
    "dna_init",
    "sequence_init",
    "quota_budget",
    "models_verify",
)


def default_answers(workflow_id: str) -> dict[str, str]:
    spec = COCKPIT_WORKFLOWS.get(workflow_id)
    if spec is None:
        return {}
    return {f.key: f.default for f in spec.fields}


def validate_answers(workflow_id: str, answers: dict[str, str]) -> list[str]:
    spec = COCKPIT_WORKFLOWS.get(workflow_id)
    if spec is None:
        return [f"Unknown workflow: {workflow_id}"]
    errors: list[str] = []
    for field in spec.fields:
        raw = (answers.get(field.key) or "").strip()
        if field.required and not raw:
            errors.append(f"{field.label} is required")
    if workflow_id == "sequence_init":
        dur = (answers.get("duration") or "60").strip() or "60"
        try:
            n = int(dur)
            if n <= 0:
                errors.append("Duration must be a positive integer")
        except ValueError:
            errors.append("Duration must be a positive integer")
    if workflow_id == "quota_budget":
        tier = (answers.get("tier") or "").strip()
        if tier and tier not in VALID_QUOTA_TIERS:
            errors.append(
                f"Unknown tier '{tier}'. Choose: {', '.join(sorted(VALID_QUOTA_TIERS))}"
            )
        rem = (answers.get("remaining") or "").strip()
        if rem:
            try:
                float(rem)
            except ValueError:
                errors.append("Remaining credits must be a number")
    return errors


def answers_to_argv(workflow_id: str, answers: dict[str, str]) -> list[str]:
    errors = validate_answers(workflow_id, answers)
    if errors:
        raise ValueError("; ".join(errors))
    if workflow_id == "bible_create":
        return [
            "create-bible",
            answers["title"].strip(),
            "--genre",
            (answers.get("genre") or "Cinematic").strip() or "Cinematic",
            "--chat-model",
            (answers.get("chat_model") or "grok-4.5").strip() or "grok-4.5",
            "--video-model",
            (answers.get("video_model") or "grok-imagine-video").strip()
            or "grok-imagine-video",
            "-o",
            (answers.get("output") or "production_bible.json").strip()
            or "production_bible.json",
        ]
    if workflow_id == "dna_init":
        argv = ["dna", "init", answers["name"].strip()]
        for key, flag in (
            ("core", "--core"),
            ("facial", "--facial"),
            ("hair", "--hair"),
            ("clothing", "--clothing"),
            ("emotion", "--emotion"),
        ):
            val = (answers.get(key) or "").strip()
            if val:
                argv.extend([flag, val])
        return argv
    if workflow_id == "sequence_init":
        dur = (answers.get("duration") or "60").strip() or "60"
        argv = ["sequence", "init", answers["name"].strip(), "-d", str(int(dur))]
        genre = (answers.get("genre") or "").strip()
        if genre:
            argv.extend(["-g", genre])
        return argv
    if workflow_id == "quota_budget":
        argv = ["quota", "budget", "--tier", answers["tier"].strip()]
        rem = (answers.get("remaining") or "").strip()
        if rem:
            argv.extend(["--remaining", rem])
        return argv
    if workflow_id == "models_verify":
        return ["models", "verify"]
    raise ValueError(f"Unknown workflow: {workflow_id}")


def summarize_action(workflow_id: str, answers: dict[str, str]) -> str:
    spec = COCKPIT_WORKFLOWS.get(workflow_id)
    label = spec.label if spec else workflow_id
    argv = answers_to_argv(workflow_id, answers)
    return f"{label}\n\nCommand:\n  cinematic-studio {' '.join(argv)}"
```

- [ ] **Step 4: Run tests — expect PASS**

Run: `pytest tests/test_tui_forms.py -v`  
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add tools/cli/tui/forms.py tests/test_tui_forms.py
git commit -m "feat(tui): pure cockpit form specs and argv mappers"
```

---

### Task 2: CommandOutput flexibility + form error formatter

**Files:**
- Modify: `tools/cli/tui/screens.py` — `CommandOutputScreen`
- Modify: `tools/cli/tui/widgets.py`
- Modify: `tests/test_tui_widgets.py`

**Interfaces:**
- Produces: `CommandOutputScreen(label: str, argv: list[str], result: CommandResult)` — deprecate requiring `LauncherEntry`; keep backward compat:

```python
def __init__(
    self,
    result: CommandResult,
    *,
    label: str | None = None,
    argv: list[str] | None = None,
    entry: LauncherEntry | None = None,
) -> None:
    if entry is not None:
        label = entry.label
        argv = list(entry.argv)
    self.label = label or "Command"
    self.argv = list(argv or result.argv)
    self.result = result
```

- Produces: `format_form_errors(errors: list[str]) -> str`

- [ ] **Step 1: Test format_form_errors**

```python
# add to tests/test_tui_widgets.py
from cli.tui.widgets import format_form_errors

def test_format_form_errors() -> None:
    text = format_form_errors(["Title is required", "Bad tier"])
    assert "Title is required" in text
    assert "Bad tier" in text
```

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Implement**

```python
# widgets.py
def format_form_errors(errors: list[str]) -> str:
    if not errors:
        return ""
    lines = ["**Validation errors:**", ""]
    for e in errors:
        lines.append(f"- {e}")
    return "\n".join(lines)
```

Update `CommandOutputScreen` as above; update Launcher `_run_entry` to pass `entry=entry` still working.

- [ ] **Step 4: pytest tests/test_tui_widgets.py tests/test_tui_catalog.py -v** — PASS

- [ ] **Step 5: Commit**

```bash
git add tools/cli/tui/screens.py tools/cli/tui/widgets.py tests/test_tui_widgets.py
git commit -m "feat(tui): generalize command output and form error formatter"
```

---

### Task 3: Cockpit menu, FormScreen, ConfirmScreen, bindings

**Files:**
- Modify: `tools/cli/tui/screens.py` (main work)
- Modify: `tools/cli/tui/app.py` (CSS, SUB_TITLE)
- Test: import smoke only (extend `test_studio_tui_importable` or add `test_cockpit_screens_importable`)

**Interfaces:**
- Consumes: Task 1 forms API, Task 2 CommandOutput + format_form_errors, runner
- Produces: `CockpitMenuScreen`, `FormScreen(workflow_id)`, `ConfirmScreen(workflow_id, answers)`

- [ ] **Step 1: Import smoke test**

```python
# tests/test_tui_forms.py or test_tui_widgets.py
def test_cockpit_screens_importable() -> None:
    from cli.tui.screens import CockpitMenuScreen, ConfirmScreen, FormScreen

    assert CockpitMenuScreen is not None
    assert FormScreen is not None
    assert ConfirmScreen is not None
```

- [ ] **Step 2: Run — expect FAIL** (missing classes)

- [ ] **Step 3: Implement screens**

Add to `screens.py`:

```python
from cli.tui.forms import (
    COCKPIT_ORDER,
    COCKPIT_WORKFLOWS,
    answers_to_argv,
    default_answers,
    summarize_action,
    validate_answers,
)
from cli.tui.widgets import format_error_panel, format_form_errors, format_home_markdown
from textual.widgets import Button, Input
```

**HomeScreen:** add `Binding("c", "cockpit", "Cockpit")` and:

```python
def action_cockpit(self) -> None:
    self.app.push_screen(CockpitMenuScreen())
```

**CockpitMenuScreen:**

```python
class CockpitMenuScreen(Screen[None]):
    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("h", "close", "Home"),
        Binding("q", "quit_app", "Quit"),
        Binding("question_mark", "help", "Help"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(
            "Cockpit — production workflows · Enter to open · Esc back",
            id="cockpit-hint",
        )
        yield ListView(
            *[
                ListItem(
                    Label(
                        f"{COCKPIT_WORKFLOWS[wid].label}  "
                        f"[dim]{COCKPIT_WORKFLOWS[wid].description}[/dim]"
                    ),
                    id=f"wf-{wid}",
                )
                for wid in COCKPIT_ORDER
            ],
            id="cockpit-list",
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        wid = item_id.removeprefix("wf-")
        spec = COCKPIT_WORKFLOWS.get(wid)
        if spec is None:
            return
        if not spec.fields and not spec.needs_confirm:
            argv = answers_to_argv(wid, {})
            result = run_cli_command(argv)
            self.app.push_screen(
                CommandOutputScreen(result=result, label=spec.label, argv=argv)
            )
            return
        self.app.push_screen(FormScreen(workflow_id=wid))

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())

    def action_quit_app(self) -> None:
        self.app.exit()
```

**FormScreen:**

```python
class FormScreen(Screen[None]):
    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, workflow_id: str) -> None:
        super().__init__()
        self.workflow_id = workflow_id
        self.spec = COCKPIT_WORKFLOWS[workflow_id]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"{self.spec.label}", id="form-title")
        yield Label(self.spec.description, id="form-desc")
        yield Static("", id="form-errors")
        with VerticalScroll(id="form-fields"):
            answers = default_answers(self.workflow_id)
            for field in self.spec.fields:
                yield Label(f"{field.label}" + (" *" if field.required else ""))
                yield Input(
                    value=answers.get(field.key, field.default),
                    placeholder=field.help or field.key,
                    id=f"field-{field.key}",
                )
        yield Button("Submit", id="form-submit", variant="primary")
        yield Button("Cancel", id="form-cancel")
        yield Footer()

    def _collect(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for field in self.spec.fields:
            widget = self.query_one(f"#field-{field.key}", Input)
            out[field.key] = widget.value
        return out

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "form-cancel":
            self.action_close()
            return
        if event.button.id == "form-submit":
            answers = self._collect()
            errors = validate_answers(self.workflow_id, answers)
            err_widget = self.query_one("#form-errors", Static)
            if errors:
                err_widget.update(format_form_errors(errors))
                return
            err_widget.update("")
            self.app.push_screen(
                ConfirmScreen(workflow_id=self.workflow_id, answers=answers)
            )

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()
```

**ConfirmScreen:**

```python
class ConfirmScreen(Screen[None]):
    BINDINGS = [
        Binding("y", "confirm", "Run"),
        Binding("n", "close", "Cancel"),
        Binding("escape", "close", "Cancel"),
        Binding("enter", "confirm", "Run"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, workflow_id: str, answers: dict[str, str]) -> None:
        super().__init__()
        self.workflow_id = workflow_id
        self.answers = answers
        self.spec = COCKPIT_WORKFLOWS[workflow_id]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(summarize_action(self.workflow_id, self.answers), id="confirm-body")
        yield Label("y / Enter = run · n / Esc = cancel", id="confirm-hint")
        yield Button("Run", id="confirm-run", variant="primary")
        yield Button("Cancel", id="confirm-cancel")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-cancel":
            self.action_close()
        elif event.button.id == "confirm-run":
            self.action_confirm()

    def action_confirm(self) -> None:
        argv = answers_to_argv(self.workflow_id, self.answers)
        result = run_cli_command(argv)
        self.app.push_screen(
            CommandOutputScreen(
                result=result,
                label=self.spec.label,
                argv=argv,
            )
        )

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()
```

**HelpScreen** text replace/add:

```
c  Open cockpit (Bible / DNA / Sequence / Quota / Models)
...
Cockpit forms confirm before write. No spend / wizard in TUI.
y/n on confirm run/cancel.
```

**app.py:**

```python
SUB_TITLE = "Dashboard · Launcher · Cockpit"
# CSS additions:
# #cockpit-hint, #form-title, #form-errors, #confirm-body, #confirm-hint { padding: 0 2; }
# #form-fields { height: 1fr; padding: 0 2; }
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_tui_forms.py tests/test_tui_widgets.py tests/test_tui_catalog.py tests/test_tui_runner.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/cli/tui/screens.py tools/cli/tui/app.py tests/
git commit -m "feat(tui): cockpit menu, forms, confirm, and models verify"
```

---

### Task 4: README + full verification

**Files:**
- Modify: `README.md` near `cinematic-studio ui`

- [ ] **Step 1: Document**

```markdown
# Interactive terminal UI (dashboard + launcher + cockpit)
cinematic-studio ui
# Cockpit (press c): Create Bible, DNA init, Sequence init, Quota budget, Models verify
# or: python tools/cinematic_studio_cli.py ui --interval 5
```

- [ ] **Step 2: Full suite**

```bash
pytest tests/test_tui_forms.py tests/test_tui_catalog.py tests/test_tui_runner.py \
  tests/test_tui_widgets.py tests/test_cli_smoke.py tests/test_cli_dashboard.py -v
```

Expected: all PASS

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: document TUI cockpit production workflows"
```

---

## Spec coverage checklist

| Spec requirement | Task |
|------------------|------|
| Pure forms API + 5 workflows | 1 |
| Argv maps + no wizard/spend | 1 |
| CommandOutput without LauncherEntry only | 2 |
| Form error banner helper | 2 |
| Cockpit menu + `c` | 3 |
| Form → Confirm → CLI | 3 |
| models_verify immediate | 3 |
| Help bindings | 3 |
| README | 4 |
| Tests without PTY | 1–4 |

## Out of scope

- Spend / submit / wizard / NSFW run  
- Streamlit  
- DNA lock / add-clip  

## Self-review notes

- `CommandOutputScreen` constructor change must keep Launcher path working (`entry=`).  
- After Confirm runs, Output is stacked; Esc pops Output then Confirm then Form — acceptable v2; optional future: pop confirm before push output.  
- `answers_to_argv` for bible requires `title` key after validation — use `.strip()` on required fields.  
- Tier set hardcoded to match design (not live import of `SUBSCRIPTION_TIERS`) to keep forms pure and fast.
