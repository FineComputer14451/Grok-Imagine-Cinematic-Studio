"""Hidden did-you-mean / forward aliases for documented ghost verbs."""

from __future__ import annotations

import typer
from typer.models import DefaultPlaceholder

from cli.help_ia import _GHOST_CTX, _info_name
from cli.plugin_commands import catalog_check
from cli.shared import console

_DNA_HINT = (
    "`dna extract` is not a CLI verb (Character DNA Extractor is a chat skill).\n"
    "Use: cinematic-studio dna init\n"
    "     cinematic-studio dna save\n"
    "     cinematic-studio dna lock\n"
    "     cinematic-studio dna handoff"
)

_EXTEND_HINT = (
    "`sequence extend` is not a CLI verb.\n"
    "Use: cinematic-studio sequence extend-prompt\n"
    "     cinematic-studio sequence add-clip\n"
    "     cinematic-studio sequence run          (Imagine spend)\n"
    "     cinematic-studio nsfw extend plan      (opt-in NSFW)"
)


def register_ghost_aliases(app: typer.Typer) -> None:
    """Attach hidden ghosts onto dna / sequence / plugin. Call after register_*."""
    dna = _require_group(app, "dna")
    seq = _require_group(app, "sequence")
    plugin = _require_group(app, "plugin")

    @dna.command(
        "extract",
        hidden=True,
        add_help_option=False,
        context_settings=_GHOST_CTX,
    )
    def dna_extract_ghost() -> None:
        console.print(_DNA_HINT)
        raise typer.Exit(2)

    @seq.command(
        "extend",
        hidden=True,
        add_help_option=False,
        context_settings=_GHOST_CTX,
    )
    def sequence_extend_ghost() -> None:
        console.print(_EXTEND_HINT)
        raise typer.Exit(2)

    plugin.command(name="check", hidden=True)(catalog_check)


def _require_group(app: typer.Typer, name: str) -> typer.Typer:
    for group_info in app.registered_groups:
        if _info_name(group_info) != name:
            continue
        inst = group_info.typer_instance
        if inst is None or isinstance(inst, DefaultPlaceholder):
            break
        return inst
    raise RuntimeError(f"CLI group {name!r} is not registered")
