"""Shared generation spend preflight for SFW/NSFW batch CLI."""

from __future__ import annotations

from typing import Any, Callable

import typer
from rich.panel import Panel

from motion_readiness import (
    MOTION_TIERS,
    apply_motion_vector_to_shot,
    evaluate_motion_brief_readiness,
    normalize_motion_tier,
)
from plate_readiness import (
    PLATE_OK,
    PLATE_STATUSES,
    evaluate_plate_lock_readiness,
    normalize_plate_status,
)
from spend_readiness import (
    evaluate_generation_spend_readiness,
    spend_hard_fail_reasons,
)

from cli.shared import console


def find_shot(batch: dict[str, Any], shot_id: str) -> dict[str, Any] | None:
    for s in batch.get("shots", []):
        if s.get("shot_id") == shot_id:
            return s
    return None


def print_readiness_child(report: dict[str, Any], *, label: str) -> None:
    for w in report.get("warnings") or []:
        console.print(f"[yellow]⚠️  {w}[/yellow]")
    if report.get("blockers"):
        for b in report["blockers"]:
            console.print(f"[yellow]⚠️  {label} blocker: {b}[/yellow]")
        if report.get("fixes"):
            console.print("[dim]Fixes:[/dim]")
            for fix in report["fixes"]:
                console.print(f"  → {fix}")


def preflight_spend(
    shot: dict[str, Any],
    *,
    strict_plate: bool = False,
    strict_motion: bool = False,
) -> dict[str, Any]:
    """Evaluate plate+motion; print notes; exit 1 if hard-fail flags trip."""
    report = evaluate_generation_spend_readiness(
        shot, strict_motion=strict_motion
    )
    plate = report.get("plate") or {}
    motion = report.get("motion") or {}
    print_readiness_child(plate, label="plate")
    print_readiness_child(motion, label="motion")
    reasons = spend_hard_fail_reasons(
        report, strict_plate=strict_plate, strict_motion=strict_motion
    )
    if reasons:
        labels = {
            "plate": "Plate lock readiness failed (--strict-plate)",
            "motion": "Motion brief readiness failed (--strict-motion)",
        }
        for r in reasons:
            console.print(f"[red]{labels.get(r, r)}[/red]")
        raise typer.Exit(1)
    return report


def register_plate_motion_commands(
    app: typer.Typer,
    *,
    load_batch: Callable[[str], dict[str, Any]],
    save_batch: Callable[[dict[str, Any]], Any],
) -> None:
    """Register plate set/show and motion set/show on a batch typer app."""
    plate_app = typer.Typer(help="Plate lock status for still→video spend")
    app.add_typer(plate_app, name="plate")
    motion_app = typer.Typer(help="Structured MOTION_VECTOR brief for video spend")
    app.add_typer(motion_app, name="motion")

    @plate_app.command("set")
    def plate_set(
        batch_name: str = typer.Argument(..., help="Batch slug or ID"),
        shot_id: str = typer.Argument(..., help="Shot ID"),
        status: str = typer.Option(..., "--status", help="draft | approved | locked"),
        path: str = typer.Option(None, "--path", help="Local plate path"),
        asset_id: str = typer.Option(None, "--asset-id", help="Curator / plate asset id"),
        reference_image_id: str = typer.Option(
            None, "--reference-image-id", help="Imagine reference_image_id"
        ),
    ):
        """Set plate_status (and optional path/ids) on a batch shot."""
        normalized = normalize_plate_status(status)
        if normalized is None or normalized not in PLATE_STATUSES:
            console.print(
                f"[red]Invalid --status:[/red] {status!r}\n"
                f"Expected one of: {', '.join(sorted(PLATE_STATUSES))}"
            )
            raise typer.Exit(1)
        batch = load_batch(batch_name)
        shot = find_shot(batch, shot_id)
        if not shot:
            console.print(f"[red]Shot not found:[/red] {shot_id}")
            raise typer.Exit(1)
        shot["plate_status"] = normalized
        if path:
            shot["plate_path"] = path
        if asset_id:
            shot["plate_asset_id"] = asset_id
            if not shot.get("reference_image_id"):
                shot["reference_image_id"] = asset_id
        if reference_image_id:
            shot["reference_image_id"] = reference_image_id
        if normalized in PLATE_OK:
            shot["has_reference"] = True
        save_batch(batch)
        console.print(
            Panel(
                f"Shot: {shot_id}\n"
                f"plate_status: {normalized}\n"
                f"plate_path: {shot.get('plate_path') or '—'}\n"
                f"plate_asset_id: {shot.get('plate_asset_id') or '—'}\n"
                f"reference_image_id: {shot.get('reference_image_id') or '—'}\n\n"
                f"OK for still→video: {normalized in PLATE_OK}",
                title="Plate set",
                border_style="green" if normalized in PLATE_OK else "yellow",
            )
        )

    @plate_app.command("show")
    def plate_show(
        batch_name: str = typer.Argument(..., help="Batch slug or ID"),
        shot_id: str = typer.Argument(..., help="Shot ID"),
    ):
        """Show plate fields and readiness for a shot."""
        batch = load_batch(batch_name)
        shot = find_shot(batch, shot_id)
        if not shot:
            console.print(f"[red]Shot not found:[/red] {shot_id}")
            raise typer.Exit(1)
        report = evaluate_plate_lock_readiness(shot)
        console.print(
            Panel(
                f"Shot: {shot_id}\n"
                f"Mode: {report.get('execution_mode') or shot.get('recommended_mode') or '—'}\n"
                f"plate_status: {shot.get('plate_status') or '—'}\n"
                f"plate_path: {shot.get('plate_path') or '—'}\n"
                f"plate_asset_id: {shot.get('plate_asset_id') or '—'}\n"
                f"reference_image_id: {shot.get('reference_image_id') or '—'}\n"
                f"has_reference: {shot.get('has_reference')}\n"
                f"Readiness pass: {report.get('pass')}",
                title="Plate show",
                border_style="green" if report.get("pass") else "yellow",
            )
        )
        print_readiness_child(report, label="plate")

    @motion_app.command("set")
    def motion_set(
        batch_name: str = typer.Argument(..., help="Batch slug or ID"),
        shot_id: str = typer.Argument(..., help="Shot ID"),
        action: str = typer.Option(..., "--action", help="Subject action / motion"),
        camera: str = typer.Option(..., "--camera", help="Camera move"),
        emotion: str = typer.Option(..., "--emotion", help="Emotional beat"),
        tier: str = typer.Option(
            None, "--tier", help="micro | medium | kinetic (optional)"
        ),
    ):
        """Set motion_vector {action, camera, emotion} on a batch shot."""
        batch = load_batch(batch_name)
        shot = find_shot(batch, shot_id)
        if not shot:
            console.print(f"[red]Shot not found:[/red] {shot_id}")
            raise typer.Exit(1)
        if tier is not None and normalize_motion_tier(tier) is None:
            console.print(
                f"[red]Invalid --tier:[/red] {tier!r}\n"
                f"Expected one of: {', '.join(sorted(MOTION_TIERS))}"
            )
            raise typer.Exit(1)
        apply_motion_vector_to_shot(
            shot, action=action, camera=camera, emotion=emotion, motion_tier=tier
        )
        save_batch(batch)
        report = evaluate_motion_brief_readiness(shot, strict=True)
        mv = shot.get("motion_vector") or {}
        console.print(
            Panel(
                f"Shot: {shot_id}\n"
                f"action: {mv.get('action')}\n"
                f"camera: {mv.get('camera')}\n"
                f"emotion: {mv.get('emotion')}\n"
                f"motion_tier: {shot.get('motion_tier') or '—'}\n"
                f"Complete triple: {report.get('complete_triple')}",
                title="Motion set",
                border_style="green" if report.get("complete_triple") else "yellow",
            )
        )

    @motion_app.command("show")
    def motion_show(
        batch_name: str = typer.Argument(..., help="Batch slug or ID"),
        shot_id: str = typer.Argument(..., help="Shot ID"),
    ):
        """Show motion brief and readiness for a shot."""
        batch = load_batch(batch_name)
        shot = find_shot(batch, shot_id)
        if not shot:
            console.print(f"[red]Shot not found:[/red] {shot_id}")
            raise typer.Exit(1)
        report = evaluate_motion_brief_readiness(shot, strict=False)
        mv = report.get("motion_vector") or {}
        console.print(
            Panel(
                f"Shot: {shot_id}\n"
                f"Mode: {report.get('execution_mode') or shot.get('recommended_mode') or '—'}\n"
                f"action: {mv.get('action') or '—'}\n"
                f"camera: {mv.get('camera') or '—'}\n"
                f"emotion: {mv.get('emotion') or '—'}\n"
                f"motion_tier: {shot.get('motion_tier') or '—'}\n"
                f"Complete triple: {report.get('complete_triple')}\n"
                f"Readiness pass (soft): {report.get('pass')}",
                title="Motion show",
                border_style="green" if report.get("pass") else "yellow",
            )
        )
        print_readiness_child(report, label="motion")
