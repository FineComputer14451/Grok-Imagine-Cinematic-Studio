"""Shared Rich output for quota / cost estimates."""

from __future__ import annotations

from typing import Any

from rich import box
from rich.table import Table

from cli.shared import console

RISK_COLORS = {"low": "green", "medium": "yellow", "high": "orange1", "critical": "red"}


def _risk_cell(risk: dict[str, Any]) -> str:
    level = risk.get("risk_level", "unknown")
    color = RISK_COLORS.get(level, "white")
    return f"[{color}]{level}[/{color}]"


def print_production_estimate_table(
    estimate: dict[str, Any],
    risk: dict[str, Any],
    *,
    title: str = "💰 Production Cost Estimate (1.5 per-second)",
    duration: int | None = None,
    complexity: str | None = None,
    resolution: str | None = None,
    fast_mode: bool | None = None,
    quality_pass: bool | None = None,
    video_model: str | None = None,
    table_box: box.Box = box.SIMPLE,
    value_style: str = "bold green",
) -> None:
    """Render a unified production cost estimate table."""
    table = Table(title=title, box=table_box)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style=value_style if value_style else "white")

    if duration is not None:
        table.add_row("Duration", f"{duration}s")
    if video_model is not None or estimate.get("video_model"):
        table.add_row("Video Model", str(estimate.get("video_model", video_model or "—")))
    table.add_row("Clips", str(estimate["clip_count"]))
    if complexity is not None:
        table.add_row("Complexity", complexity.title())
    if resolution is not None:
        table.add_row("Resolution", resolution)
    if fast_mode is not None:
        table.add_row("Fast Mode", str(fast_mode))
    if quality_pass is not None:
        table.add_row("Quality Pass", str(quality_pass))
    if estimate.get("avg_clip_duration") is not None and duration is None:
        table.add_row("Avg Clip", f"{estimate['avg_clip_duration']}s")
    table.add_row("Credits", f"{estimate['credits_low']} – {estimate['credits_high']}")
    table.add_row("Est. USD", f"${estimate['usd_low']} – ${estimate['usd_high']}")
    table.add_row("Est. Tokens", f"~{estimate['estimated_tokens']:,}")
    table.add_row("Risk", _risk_cell(risk))
    console.print(table)