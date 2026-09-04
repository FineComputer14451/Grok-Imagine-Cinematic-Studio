"""Central CLI help information architecture (journey panels + examples).

Stamps Typer ``rich_help_panel`` after command registration so ``--help``
groups stay scannable without renaming argv. ``StudioGroup`` sorts commands
so Rich first-seen panel order matches ``ROOT_PANEL_ORDER`` / nested maps.
"""

from __future__ import annotations

import inspect
from typing import Any

import typer
from typer.core import TyperGroup
from typer.models import CommandInfo, DefaultPlaceholder, TyperInfo

from cli.shared import STUDIO_VERSION

ROOT_PANEL_ORDER: tuple[str, ...] = (
    "Orient",
    "Health",
    "Produce",
    "Spend",
    "Gate",
    "Deliver",
    "Surfaces",
    "Meta",
)

NESTED_PANEL_ORDER: dict[str, tuple[str, ...]] = {
    "dna": ("Setup", "Lock", "Inject"),
    "sequence": ("Setup", "Extend", "Gate", "Deliver"),
    "plugin": ("Catalog", "Inspect", "Hygiene"),
    "imagine": ("Jobs", "Handoff", "Artifacts"),
    "files": ("Inspect", "Store"),
    "quota": ("Health", "Spend"),
    "sfw": ("Plan", "Readiness", "Spend", "Quality"),
    "nsfw": ("Plan", "Readiness", "Spend", "Quality", "Extend"),
    "wave-a": ("Packets", "Gate"),
}

ROOT_MAP: dict[str, str] = {
    "dashboard": "Orient",
    "commands": "Orient",
    "status": "Orient",
    "version": "Orient",
    "activate": "Orient",
    "list-agents": "Orient",
    "list-role-cards": "Orient",
    "show-role-card": "Orient",
    "doctor": "Health",
    "validate": "Health",
    "models": "Health",
    "stack": "Health",
    "quota": "Health",
    "grok": "Health",
    "create-bible": "Produce",
    "generate-prompt": "Produce",
    "dna": "Produce",
    "sequence": "Produce",
    "animatic": "Produce",
    "wave-a": "Produce",
    "memory": "Produce",
    "sfw": "Spend",
    "nsfw": "Spend",
    "imagine": "Spend",
    "files": "Spend",
    "generation": "Spend",
    "cost-simulate": "Spend",
    "handoff": "Gate",
    "report": "Deliver",
    "ui": "Surfaces",
    "web": "Surfaces",
    "web-react": "Surfaces",
    "api": "Surfaces",
    "plugin": "Meta",
}

NESTED_MAPS: dict[str, dict[str, str]] = {
    "dna": {
        "init": "Setup",
        "save": "Setup",
        "list": "Setup",
        "show": "Setup",
        "handoff": "Lock",
        "lock": "Lock",
        "inject": "Inject",
    },
    "sequence": {
        "init": "Setup",
        "list": "Setup",
        "show": "Setup",
        "add-clip": "Setup",
        "handoff": "Extend",
        "extend-prompt": "Extend",
        "run": "Extend",
        "regen": "Extend",
        "replan": "Extend",
        "memory": "Extend",
        "temp": "Extend",
        "cast": "Extend",
        "qa": "Gate",
        "qa-assist": "Gate",
        "drift-score": "Gate",
        "seam-report": "Gate",
        "amv-check": "Gate",
        "continuity-diff": "Gate",
        "estimate-cost": "Gate",
        "health": "Gate",
        "color-grade": "Deliver",
        "polish": "Deliver",
        "deliver": "Deliver",
        "edl": "Deliver",
        "artifact-lexicon": "Deliver",
    },
    "plugin": {
        "catalog": "Catalog",
        "packs": "Inspect",
        "status": "Inspect",
        "list": "Inspect",
        "declutter": "Hygiene",
    },
    "imagine": {
        "submit": "Jobs",
        "status": "Jobs",
        "poll": "Jobs",
        "list": "Jobs",
        "cancel": "Jobs",
        "region": "Jobs",
        "verify": "Jobs",
        "bridge": "Handoff",
        "agent-handoff": "Handoff",
        "workflow": "Handoff",
        "artifact": "Artifacts",
        "artifacts": "Artifacts",
        "report": "Artifacts",
    },
    "files": {
        "list": "Inspect",
        "get": "Inspect",
        "upload": "Store",
        "delete": "Store",
    },
    "quota": {
        "dashboard": "Health",
        "sync": "Health",
        "reconcile": "Health",
        "budget": "Health",
        "optimize": "Health",
        "estimate": "Spend",
        "clip": "Spend",
        "sequence": "Spend",
        "record": "Spend",
    },
    "sfw": {
        "plan": "Plan",
        "list": "Plan",
        "next": "Plan",
        "decide": "Plan",
        "plate": "Readiness",
        "motion": "Readiness",
        "run": "Spend",
        "session": "Spend",
        "record": "Spend",
        "promote": "Quality",
        "quality-pending": "Quality",
        "retry": "Quality",
    },
    "nsfw": {
        "attest": "Plan",
        "plan": "Plan",
        "list": "Plan",
        "next": "Plan",
        "decide": "Plan",
        "plate": "Readiness",
        "motion": "Readiness",
        "run": "Spend",
        "session": "Spend",
        "record": "Spend",
        "promote": "Quality",
        "quality-pending": "Quality",
        "retry": "Quality",
        "report": "Quality",
        "extend": "Extend",
    },
    "wave-a": {
        "plate-motion": "Packets",
        "contact": "Packets",
        "hmu": "Packets",
        "dialogue": "Packets",
        "score": "Packets",
        "title": "Packets",
        "crop": "Packets",
        "briefs": "Packets",
        "validate": "Gate",
        "attach": "Gate",
    },
}

ROOT_HELP = (
    f"🎥 Grok Imagine Cinematic Studio v{STUDIO_VERSION} — "
    "Grok 4.6 cinematic+Build · optional 4.3 1M · Imagine 1.0/1.5 · 25-agent core CLI\n\n"
    "Orient    cinematic-studio dashboard\n"
    "Health    cinematic-studio doctor --quick\n"
    "Produce   cinematic-studio create-bible --wizard\n"
    "Spend     cinematic-studio quota estimate -d 30\n"
    "Gate      cinematic-studio handoff validate PACKET.json --strict-handoff\n"
    "Deliver   cinematic-studio sequence polish NAME --dry-run\n"
    "Surfaces  cinematic-studio ui"
)

ROOT_EPILOG = (
    "PATH wrapper (not Typer): cinematic-studio install | update | verify | declutter\n"
    "\n"
    "→ bash scripts/cinematic_studio.sh …\n"
    "\n"
    "Full command reference: docs/CLI_REFERENCE.md"
)

_GHOST_CTX = {
    "allow_extra_args": True,
    "ignore_unknown_options": True,
}


class StudioGroup(TyperGroup):
    """Sort subcommands by journey panel, then name, so Rich panel order is stable."""

    def list_commands(self, ctx: Any) -> list[str]:
        names = [n for n in self.commands]
        order = _panel_order_for(self.name or "")
        index = {panel: i for i, panel in enumerate(order)}

        def sort_key(name: str) -> tuple[int, str]:
            cmd = self.commands.get(name)
            panel = getattr(cmd, "rich_help_panel", None) or ""
            return (index.get(str(panel), len(index)), name)

        return sorted(names, key=sort_key)


def apply_help_ia(app: typer.Typer) -> None:
    """Stamp ``rich_help_panel`` on registered commands/groups. Call after register_*."""
    _apply_level(app, ROOT_MAP, label="root")
    for group_info in app.registered_groups:
        name = _info_name(group_info)
        nested = NESTED_MAPS.get(name)
        if nested is None:
            continue
        inst = group_info.typer_instance
        if inst is None or isinstance(inst, DefaultPlaceholder):
            continue
        group_info.cls = StudioGroup
        _apply_level(inst, nested, label=name)


def _panel_order_for(group_name: str) -> tuple[str, ...]:
    return NESTED_PANEL_ORDER.get(group_name, ROOT_PANEL_ORDER)


def _apply_level(typer_app: typer.Typer, mapping: dict[str, str], *, label: str) -> None:
    unmapped: list[str] = []
    for command_info in typer_app.registered_commands:
        if command_info.hidden:
            continue
        name = _info_name(command_info)
        panel = mapping.get(name)
        if panel is None:
            unmapped.append(name)
            continue
        command_info.rich_help_panel = panel
    for group_info in typer_app.registered_groups:
        if _is_hidden(group_info):
            continue
        name = _info_name(group_info)
        panel = mapping.get(name)
        if panel is None:
            unmapped.append(name)
            continue
        group_info.rich_help_panel = panel
    if unmapped:
        missing = ", ".join(sorted(unmapped))
        raise RuntimeError(f"help IA map incomplete for {label}: {missing}")


def _info_name(info: CommandInfo | TyperInfo | Any) -> str:
    name = getattr(info, "name", None)
    if isinstance(name, str) and name:
        return name
    callback = getattr(info, "callback", None)
    cb_name = getattr(callback, "__name__", "") if callback is not None else ""
    if cb_name:
        return cb_name.replace("_", "-")
    return ""


def _is_hidden(info: Any) -> bool:
    hidden = getattr(info, "hidden", False)
    if isinstance(hidden, DefaultPlaceholder):
        return bool(hidden.value)
    return bool(hidden)


def collect_catalog(
    typer_app: typer.Typer, prefix: tuple[str, ...] = ()
) -> list[tuple[str, str]]:
    """Visible command paths and one-line summaries (hidden ghosts omitted)."""
    rows: list[tuple[str, str]] = []
    for command_info in typer_app.registered_commands:
        if command_info.hidden:
            continue
        name = _info_name(command_info)
        if not name:
            continue
        rows.append((" ".join((*prefix, name)), _help_text(command_info)))
    for group_info in typer_app.registered_groups:
        if _is_hidden(group_info):
            continue
        name = _info_name(group_info)
        if not name:
            continue
        path = " ".join((*prefix, name))
        rows.append((path, _help_text(group_info)))
        inst = getattr(group_info, "typer_instance", None)
        if inst is None or isinstance(inst, DefaultPlaceholder):
            continue
        rows.extend(collect_catalog(inst, (*prefix, name)))
    return rows


def filter_catalog(rows: list[tuple[str, str]], query: str) -> list[tuple[str, str]]:
    tokens = query.strip().lower().split()
    if not tokens:
        return rows
    hits: list[tuple[str, str]] = []
    for path, summary in rows:
        blob = f"{path} {summary}".lower()
        if all(token in blob for token in tokens):
            hits.append((path, summary))
    return hits


def _unwrap(value: Any) -> Any:
    if isinstance(value, DefaultPlaceholder):
        return value.value
    return value


def _first_line(text: str) -> str:
    return text.strip().split("\n", 1)[0]


def _help_text(info: Any) -> str:
    raw = _unwrap(getattr(info, "help", None))
    if isinstance(raw, str) and raw.strip():
        return _first_line(raw)
    callback = _unwrap(getattr(info, "callback", None))
    if callable(callback):
        doc = inspect.getdoc(callback) or ""
        if doc.strip() and "You shouldn't use this class directly" not in doc:
            return _first_line(doc)
    inst = _unwrap(getattr(info, "typer_instance", None))
    if inst is None:
        return ""
    inst_info = getattr(inst, "info", None)
    inner = _unwrap(getattr(inst_info, "help", None) if inst_info is not None else None)
    if isinstance(inner, str) and inner.strip():
        return _first_line(inner)
    return ""
