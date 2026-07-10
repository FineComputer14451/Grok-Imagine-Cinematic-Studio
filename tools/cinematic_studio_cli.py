#!/usr/bin/env python3
"""
Grok Imagine Cinematic Studio CLI v3.7.1 — Enhanced Edition
Professional multi-agent cinematic production toolkit with Role Card integration
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cli.bible_commands import register as register_bible_commands  # noqa: E402
from cli.dna_commands import register as register_dna_commands  # noqa: E402
from cli.models_commands import models_app  # noqa: E402
from cli.animatic_commands import register as register_animatic_commands  # noqa: E402
from cli.imagine_commands import register as register_imagine_commands  # noqa: E402
from cli.nsfw_commands import register as register_nsfw_commands  # noqa: E402
from cli.quota_commands import register as register_quota_commands  # noqa: E402
from cli.sfw_commands import register as register_sfw_commands  # noqa: E402
from cli.plugin_commands import register as register_plugin_commands  # noqa: E402
from cli.report_commands import register as register_report_commands  # noqa: E402
from cli.sequence_commands import register as register_sequence_commands  # noqa: E402
from cli.studio_commands import register as register_studio_commands  # noqa: E402

app = typer.Typer(
    name="cinematic-studio",
    help="🎥 Grok Imagine Cinematic Studio v3.6 — Full 23-Agent Cinematic Production CLI",
    add_completion=False,
    rich_markup_mode="rich",
)

dna_app = typer.Typer(help="Character DNA extraction, Identity Lock handoff, and prompt injection")
seq_app = typer.Typer(help="Long-form 1.5 extend/stitch sequencing, handoffs, and chain QA")
quota_app = typer.Typer(help="Per-second 1.5 quota estimation, budgeting, and optimization")
nsfw_app = typer.Typer(help="Quota-aware NSFW batch planning, sequence extension, and daily reports")
extend_app = typer.Typer(help="Sensual sequence extension 30-120s+ from reference frame or short clip")
sfw_app = typer.Typer(help="SFW batch planning with hero-first tiers and Reference Curator routing")
imagine_app = typer.Typer(help="Imagine API jobs — submit, poll, and track generation queue")
animatic_app = typer.Typer(help="Animatic pre-vis boards and hero promotion workflow")

app.add_typer(dna_app, name="dna")
app.add_typer(seq_app, name="sequence")
app.add_typer(quota_app, name="quota")
app.add_typer(models_app, name="models")
app.add_typer(nsfw_app, name="nsfw")
app.add_typer(sfw_app, name="sfw")
app.add_typer(imagine_app, name="imagine")
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
register_animatic_commands(animatic_app)
register_report_commands(app)
register_plugin_commands(app)

if __name__ == "__main__":
    app()