# PR3 — `studio_core.services.execute`

## Goal

One safe entrypoint for running registered ActionSpec actions from any shell:

| Mode | Who uses it | Mechanism |
|------|-------------|-----------|
| `subprocess` | Textual TUI | `python tools/cinematic_studio_cli.py …` |
| `inprocess` | Web / API (default) | Typer `CliRunner` invoke (no process spawn) |

Both paths share `validate_answers` → `answers_to_argv` → forbidden-token checks.

## API

```python
from studio_core.services.execute import execute_action, ActionResult

r: ActionResult = execute_action("status", mode="inprocess")
r = execute_action("dna_lock", {"name": "Hero"}, mode="subprocess", timeout=60)
assert r.ok and r.returncode == 0
print(r.stdout)
```

## Compatibility

- `cli.tui.runner.run_action` / `run_cli_command` still return `CommandResult`
- They now delegate to `execute_*` with `mode="subprocess"`
- Existing TUI tests should pass unchanged

## Verify

```bash
pytest tests/test_studio_core_execute.py tests/test_tui_runner.py -q
```

## Out of scope

- Direct domain-function dispatch (bypass Typer) — later optimization
- FastAPI route wrappers
- Streamlit wiring
