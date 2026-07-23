"""Grok Build / xAI model registry CLI commands (Grok 4.5 default)."""

from __future__ import annotations

import typer
from rich import box
from rich.panel import Panel
from rich.table import Table

from models import (
    DEFAULT_GROK_BUILD_MODEL,
    DEFAULT_IMAGINE_IMAGE_MODEL,
    DEFAULT_IMAGINE_VIDEO_MODEL,
    DEFAULT_XAI_CHAT_MODEL,
    GROK_BUILD_CLI_MODELS,
    GROK_BUILD_FORK_MODEL,
    GROK_BUILD_NSFW_MODELS,
    IMAGINE_IMAGE_MODELS,
    IMAGINE_VIDEO_MODELS,
    RECOMMENDED_GROK_BUILD_CLI_VERSION,
    XAI_CHAT_MODELS,
    build_video_pipeline_spec,
    is_build_default,
    is_cinematic_default,
    model_stack_summary,
    verify_model_compatibility,
)
from cli.shared import MODELS_DOC, MODEL_LAYER_DOC, STUDIO_VERSION, console, format_stack_panel

models_app = typer.Typer(
    help="Grok Build and xAI model registry (Grok 4.5 cinematic+Build default)"
)


def _chat_tags(slug: str, info: dict) -> str:
    tags: list[str] = []
    if is_cinematic_default(slug):
        tags.append("★ cinematic default")
    if is_build_default(slug):
        tags.append("build default")
    if info.get("role") == "long_context":
        tags.append("1M opt-in")
    if info.get("deprecated"):
        tags.append("legacy")
    return f" ({', '.join(tags)})" if tags else ""


def _ordered_chat_slugs() -> list[str]:
    keys = list(XAI_CHAT_MODELS.keys())
    if DEFAULT_XAI_CHAT_MODEL in keys:
        return [DEFAULT_XAI_CHAT_MODEL] + [k for k in keys if k != DEFAULT_XAI_CHAT_MODEL]
    return keys


def _ordered_video_slugs() -> list[str]:
    keys = list(IMAGINE_VIDEO_MODELS.keys())
    if DEFAULT_IMAGINE_VIDEO_MODEL in keys:
        return [DEFAULT_IMAGINE_VIDEO_MODEL] + [
            k for k in keys if k != DEFAULT_IMAGINE_VIDEO_MODEL
        ]
    return keys


@models_app.command("list")
def models_list():
    """List Grok Build CLI, xAI chat, and Imagine model slugs (4.5 / 1.0 first)."""
    table = Table(
        title=f"🤖 Model Registry · Grok 4.5 · studio v{STUDIO_VERSION}",
        box=box.ROUNDED,
    )
    table.add_column("Category", style="bold cyan", no_wrap=True)
    table.add_column("Slug", style="green")
    table.add_column("Label / Rate", style="white")

    table.add_row(
        "Grok Build CLI (default)",
        DEFAULT_GROK_BUILD_MODEL,
        GROK_BUILD_CLI_MODELS[DEFAULT_GROK_BUILD_MODEL]["label"],
    )
    table.add_row(
        "Grok Build CLI (fork)",
        GROK_BUILD_FORK_MODEL,
        GROK_BUILD_CLI_MODELS[GROK_BUILD_FORK_MODEL]["label"],
    )
    table.add_row(
        "Grok Build CLI (recommended)",
        RECOMMENDED_GROK_BUILD_CLI_VERSION,
        "Binary version (soft probe in models verify) — not an API slug",
    )
    for slug in _ordered_chat_slugs():
        info = XAI_CHAT_MODELS[slug]
        ctx = info.get("context_tokens")
        ctx_s = f" · {ctx // 1000}k ctx" if isinstance(ctx, int) else ""
        table.add_row(
            "xAI Chat",
            slug + _chat_tags(slug, info),
            f"{info['label']}{ctx_s} — "
            f"${info['input_usd_per_1m']}/${info['output_usd_per_1m']} per 1M",
        )
    for slug in _ordered_video_slugs():
        info = IMAGINE_VIDEO_MODELS[slug]
        default = " (★ cost default)" if slug == DEFAULT_IMAGINE_VIDEO_MODEL else ""
        audio = " + native audio" if info.get("native_audio") else ""
        aliases = ", ".join(info.get("aliases", [])[:3])
        if len(info.get("aliases", [])) > 3:
            aliases += ", …"
        detail = f"{info['label']} — ${info['usd_per_second']}/sec{audio}"
        if aliases:
            detail += f"\n[dim]aliases: {aliases}[/dim]"
        table.add_row("Imagine Video", slug + default, detail)
    for slug, info in IMAGINE_IMAGE_MODELS.items():
        default = " (default)" if slug == DEFAULT_IMAGINE_IMAGE_MODEL else ""
        aliases = ", ".join(info.get("aliases", [])[:3])
        if len(info.get("aliases", [])) > 3:
            aliases += ", …"
        detail = f"{info['label']} — ${info['usd_per_image']}/image"
        if aliases:
            detail += f"\n[dim]aliases: {aliases}[/dim]"
        table.add_row("Imagine Image", slug + default, detail)

    for slug, info in GROK_BUILD_NSFW_MODELS.items():
        base = info.get("base_model", "?")
        temp = info.get("temperature")
        temp_s = f" · T={temp}" if temp is not None else ""
        aliases = ", ".join(info.get("aliases", [])[:3])
        detail = f"{info['label']} → {base}{temp_s} — {info.get('description', '')}"
        if aliases:
            detail += f"\n[dim]aliases: {aliases}[/dim]"
        table.add_row("Grok Build NSFW (opt-in)", slug, detail)

    console.print(table)
    console.print(
        f"\n[dim]Docs: {MODELS_DOC} · {MODEL_LAYER_DOC} · "
        f"opt-in 1M: --chat-model grok-4.3 · never treat CLI 0.2.93 as a model slug · "
        f"NSFW Build aliases: bash scripts/install_nsfw_grok_models.sh · "
        f"not Imagine generators[/dim]"
    )


@models_app.command("stack")
def models_stack(
    json_output: bool = typer.Option(False, "--json", help="Emit JSON"),
):
    """Show resolved model_stack + VIDEO_PIPELINE_SPEC (Grok 4.5 defaults)."""
    stack = model_stack_summary()
    if json_output:
        import json

        console.print(
            json.dumps(
                {
                    "studio_version": STUDIO_VERSION,
                    "model_stack": stack,
                    "video_pipeline_spec": build_video_pipeline_spec(
                        stack.get("imagine_video")
                    ),
                },
                indent=2,
            )
        )
        return
    console.print(format_stack_panel(stack))


@models_app.command("verify")
def models_verify():
    """Verify stack: Grok 4.5 cinematic+Build + optional 4.3 1M + Imagine 1.0/1.5."""
    result = verify_model_compatibility()
    stack = result["model_stack"]
    warn_block = ""
    if result.get("warnings"):
        warn_block += "\n\n[yellow]Warnings:[/yellow]\n" + "\n".join(
            f"• {w}" for w in result["warnings"]
        )
    if result.get("notes"):
        warn_block += "\n\n[dim]Notes:[/dim]\n" + "\n".join(
            f"• {n}" for n in result["notes"]
        )
    installed = result.get("installed_grok_cli_version") or "not found"
    if result["compatible"]:
        console.print(
            Panel.fit(
                "[bold green]✅ Model compatibility verified[/bold green]\n\n"
                f"Studio target: v{result['studio_version']}\n"
                f"Grok Build CLI: {stack['grok_build_cli_default']} "
                f"(+ {stack['grok_build_cli_fork']}, recommend ≥ "
                f"{stack.get('grok_build_cli_min_version', RECOMMENDED_GROK_BUILD_CLI_VERSION)})\n"
                f"Installed CLI: {installed}\n"
                f"xAI Chat (cinematic): {stack['xai_chat']} | Build/coding: {stack['xai_build']}\n"
                f"Imagine Video: {stack['imagine_video']} | Image: {stack['imagine_image']}\n\n"
                f"{result['video_pipeline_spec']}"
                f"{warn_block}",
                title="Grok 4.5 Cinematic+Build · Optional 4.3 1M · Imagine",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                "[bold red]❌ Model compatibility issues[/bold red]\n\n"
                + "\n".join(f"• {issue}" for issue in result["issues"])
                + warn_block,
                title="Compatibility Check Failed",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)
