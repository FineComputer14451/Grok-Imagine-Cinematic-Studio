"""Grok Build / xAI model registry CLI commands."""

from __future__ import annotations

import typer
from rich import box
from rich.panel import Panel
from rich.table import Table

from models import (
    DEFAULT_GROK_BUILD_MODEL,
    GROK_BUILD_CLI_MODELS,
    GROK_BUILD_FORK_MODEL,
    IMAGINE_IMAGE_MODELS,
    IMAGINE_VIDEO_MODELS,
    XAI_CHAT_MODELS,
    verify_model_compatibility,
)
from cli.shared import console

models_app = typer.Typer(help="Grok Build and xAI model registry")


@models_app.command("list")
def models_list():
    """List Grok Build CLI, xAI chat, and Imagine model slugs."""
    table = Table(title="🤖 Grok Build & xAI Model Registry", box=box.ROUNDED)
    table.add_column("Category", style="bold cyan", no_wrap=True)
    table.add_column("Slug", style="green")
    table.add_column("Label / Rate", style="white")

    table.add_row("Grok Build CLI (default)", DEFAULT_GROK_BUILD_MODEL, GROK_BUILD_CLI_MODELS[DEFAULT_GROK_BUILD_MODEL]["label"])
    table.add_row("Grok Build CLI (fork)", GROK_BUILD_FORK_MODEL, GROK_BUILD_CLI_MODELS[GROK_BUILD_FORK_MODEL]["label"])
    for slug, info in XAI_CHAT_MODELS.items():
        default = " (default)" if info.get("default") else ""
        table.add_row("xAI Chat", slug + default, f"{info['label']} — ${info['input_usd_per_1m']}/${info['output_usd_per_1m']} per 1M")
    for slug, info in IMAGINE_VIDEO_MODELS.items():
        default = " (default)" if info.get("default") else ""
        audio = " + native audio" if info.get("native_audio") else ""
        aliases = ", ".join(info.get("aliases", [])[:3])
        if len(info.get("aliases", [])) > 3:
            aliases += ", …"
        detail = f"{info['label']} — ${info['usd_per_second']}/sec{audio}"
        if aliases:
            detail += f"\n[dim]aliases: {aliases}[/dim]"
        table.add_row("Imagine Video", slug + default, detail)
    for slug, info in IMAGINE_IMAGE_MODELS.items():
        default = " (default)" if info.get("default") else ""
        table.add_row("Imagine Image", slug + default, f"{info['label']} — ${info['usd_per_image']}/image")

    console.print(table)
    console.print("\n[dim]Full registry: references/MODELS_v3.6.md[/dim]")


@models_app.command("verify")
def models_verify():
    """Verify Grok 4.3 + Imagine 1.5 + Grok Build model compatibility."""
    result = verify_model_compatibility()
    stack = result["model_stack"]
    if result["compatible"]:
        console.print(Panel.fit(
            "[bold green]✅ Model compatibility verified[/bold green]\n\n"
            f"Studio target: v{result['studio_version']}\n"
            f"Grok Build CLI: {stack['grok_build_cli_default']} (+ {stack['grok_build_cli_fork']})\n"
            f"xAI Chat: {stack['xai_chat']} | Build API: {stack['xai_build']}\n"
            f"Imagine Video: {stack['imagine_video']} | Image: {stack['imagine_image']}\n\n"
            f"{result['video_pipeline_spec']}",
            title="Grok 4.3 + Imagine 1.5 + Grok Build",
            border_style="green",
        ))
    else:
        console.print(Panel.fit(
            "[bold red]❌ Model compatibility issues[/bold red]\n\n"
            + "\n".join(f"• {issue}" for issue in result["issues"]),
            title="Compatibility Check Failed",
            border_style="red",
        ))
        raise typer.Exit(code=1)