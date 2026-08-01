#!/usr/bin/env python3
"""Grok Imagine Cinematic Studio CLI v3.8.9 — Grok 4.5 stack (wiring only)."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cli.animatic_commands import register as register_animatic_commands  # noqa: E402
from cli.bible_commands import register as register_bible_commands  # noqa: E402
from cli.dna_commands import register as register_dna_commands  # noqa: E402
from cli.imagine_commands import register as register_imagine_commands  # noqa: E402
from cli.models_commands import models_app  # noqa: E402
from cli.nsfw_commands import register as register_nsfw_commands  # noqa: E402
from cli.plugin_commands import register as register_plugin_commands  # noqa: E402
from cli.quota_commands import register as register_quota_commands  # noqa: E402
from cli.report_commands import register as register_report_commands  # noqa: E402
from cli.sequence_commands import register as register_sequence_commands  # noqa: E402
from cli.sfw_commands import register as register_sfw_commands  # noqa: E402
from cli.shared import STUDIO_VERSION  # noqa: E402
from cli.studio_commands import register as register_studio_commands  # noqa: E402
from cli.tui_commands import register as register_tui_commands  # noqa: E402
from cli.generation_commands import register as register_generation_commands  # noqa: E402
from cli.wave_a_commands import register as register_wave_a_commands  # noqa: E402
from cli.grok_cli_commands import register as register_grok_cli_commands  # noqa: E402
from cli.handoff_commands import register as register_handoff_commands  # noqa: E402

app = typer.Typer(
    name="cinematic-studio",
    help=(
        f"🎥 Grok Imagine Cinematic Studio v{STUDIO_VERSION} — "
        "Grok 4.5 cinematic+Build · optional 4.3 1M · Imagine 1.0/1.5 · 25-agent core CLI"
    ),
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

dna_app = typer.Typer(help="Character DNA, Identity Lock handoff, prompt injection")
seq_app = typer.Typer(help="Long-form extend/stitch, chain QA, health (1.0 cost · 1.5 audio)")
quota_app = typer.Typer(help="Quota estimation, budgeting, optimization")
nsfw_app = typer.Typer(help="NSFW batch planning, extension, daily reports")
extend_app = typer.Typer(help="Sensual sequence extension 30–120s+")
sfw_app = typer.Typer(help="SFW hero-first batches + Reference Curator routing")
imagine_app = typer.Typer(help="Imagine jobs, bridge, agent-handoff")
handoff_app = typer.Typer(help="Handoff packet validate (identity / sequence / agent-mode)")
animatic_app = typer.Typer(help="Animatic pre-vis and hero promotion")

app.add_typer(dna_app, name="dna")
app.add_typer(seq_app, name="sequence")
app.add_typer(quota_app, name="quota")
app.add_typer(models_app, name="models")
app.add_typer(nsfw_app, name="nsfw")
app.add_typer(sfw_app, name="sfw")
app.add_typer(imagine_app, name="imagine")
app.add_typer(handoff_app, name="handoff")
app.add_typer(animatic_app, name="animatic")
nsfw_app.add_typer(extend_app, name="extend")

register_studio_commands(app)
register_bible_commands(app)
register_dna_commands(dna_app)
register_sequence_commands(seq_app)
register_quota_commands(quota_app)
register_nsfw_commands(nsfw_app, extend_app)
register_sfw_commands(sfw_app)
register_imagine_commands(imagine_app)
register_handoff_commands(handoff_app)
register_animatic_commands(animatic_app)
register_report_commands(app)
register_plugin_commands(app)
register_tui_commands(app)
register_generation_commands(app)
register_wave_a_commands(app)
register_grok_cli_commands(app)

if __name__ == "__main__":
    app()
