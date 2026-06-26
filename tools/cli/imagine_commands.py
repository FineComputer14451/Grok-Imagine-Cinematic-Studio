"""Imagine API client and job queue CLI commands."""

from __future__ import annotations

import json

import typer
from rich import box
from rich.panel import Panel
from rich.table import Table

from imagine_client import (
    ImagineAPIError,
    edit_image,
    extract_image_url,
    extract_video_url,
    generate_image,
    is_dry_run,
    poll_video_job,
    submit_video_generation,
)
from imagine_jobs import cancel_job, create_job, get_job, job_summary, list_jobs, transition_job
from imagine_regions import IMAGINE_REGIONS, get_active_region, get_failover_chain, set_imagine_region
from models import DEFAULT_IMAGINE_IMAGE_MODEL, DEFAULT_IMAGINE_VIDEO_MODEL

from cli.shared import console


def register(app: typer.Typer) -> None:
    @app.command("submit")
    def imagine_submit(
        job_type: str = typer.Argument(..., help="image | image_edit | video"),
        prompt: str = typer.Option(..., "--prompt", "-p"),
        model: str = typer.Option(None, "--model", "-m"),
        image_url: str = typer.Option(None, "--image-url", help="Source image for edit or i2v"),
        duration: int = typer.Option(10, "--duration", "-d", help="Video duration seconds"),
        sequence: str = typer.Option(None, "--sequence", help="Link to sequence slug"),
        clip: str = typer.Option(None, "--clip", help="Link to clip ID"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Force mock response"),
    ):
        """Submit an Imagine generation job and track it in the job queue."""
        if job_type not in ("image", "image_edit", "video"):
            console.print("[red]job_type must be: image, image_edit, or video[/red]")
            raise typer.Exit(1)

        img_model = model or DEFAULT_IMAGINE_IMAGE_MODEL
        vid_model = model or DEFAULT_IMAGINE_VIDEO_MODEL
        slug = img_model if job_type in ("image", "image_edit") else vid_model

        job = create_job(
            job_type,
            prompt=prompt,
            model=slug,
            sequence_slug=sequence,
            clip_id=clip,
        )
        transition_job(job["job_id"], "running", dry_run=dry_run or is_dry_run())

        try:
            force_dry = dry_run or is_dry_run()
            if job_type == "image":
                resp = generate_image(prompt, model=img_model, dry_run=force_dry)
                url = extract_image_url(resp)
                transition_job(job["job_id"], "approved", result_url=url)
            elif job_type == "image_edit":
                if not image_url:
                    console.print("[red]--image-url required for image_edit[/red]")
                    raise typer.Exit(1)
                resp = edit_image(prompt, image_url=image_url, model=img_model, dry_run=force_dry)
                url = extract_image_url(resp)
                transition_job(job["job_id"], "approved", result_url=url)
            else:
                resp = submit_video_generation(
                    prompt,
                    model=vid_model,
                    duration=duration,
                    image_url=image_url,
                    dry_run=force_dry,
                )
                request_id = resp.get("request_id")
                if resp.get("status") == "done" or force_dry:
                    url = extract_video_url(resp)
                    transition_job(job["job_id"], "qa_pending", request_id=request_id, result_url=url)
                else:
                    result = poll_video_job(request_id)
                    url = extract_video_url(result)
                    transition_job(job["job_id"], "qa_pending", request_id=request_id, result_url=url)

            updated = get_job(job["job_id"])
            mode = "[yellow]DRY-RUN[/yellow]" if updated.get("dry_run") else "[green]LIVE[/green]"
            console.print(Panel(
                f"Job: {job['job_id']}\n"
                f"Type: {job_type}\n"
                f"Mode: {mode}\n"
                f"Status: {updated.get('status')}\n"
                f"URL: {updated.get('result_url', '—')}",
                title="Imagine Job Submitted",
                border_style="cyan",
            ))
        except ImagineAPIError as exc:
            transition_job(job["job_id"], "failed", error=str(exc))
            console.print(f"[red]Failed:[/red] {exc}")
            raise typer.Exit(1) from exc


    @app.command("status")
    def imagine_status(job_id: str = typer.Argument(..., help="Job ID")):
        """Show Imagine job status."""
        job = get_job(job_id)
        if not job:
            console.print(f"[red]Job not found:[/red] {job_id}")
            raise typer.Exit(1)

        table = Table(title=f"Imagine Job — {job_id}", box=box.ROUNDED)
        table.add_column("Field", style="cyan")
        table.add_column("Value")
        for key in ("job_type", "status", "model", "sequence_slug", "clip_id", "request_id", "result_url", "dry_run", "error"):
            val = job.get(key)
            if val is not None:
                table.add_row(key, str(val))
        console.print(table)
        if job.get("chain_qa"):
            console.print(Panel(json.dumps(job["chain_qa"], indent=2)[:2000], title="Chain QA", border_style="yellow"))


    @app.command("list")
    def imagine_list(
        status: str = typer.Option(None, "--status", "-s"),
        sequence: str = typer.Option(None, "--sequence"),
        limit: int = typer.Option(20, "--limit", "-n"),
    ):
        """List Imagine generation jobs."""
        jobs = list_jobs(status=status, sequence_slug=sequence, limit=limit)
        summary = job_summary()

        table = Table(title="Imagine Jobs", box=box.SIMPLE)
        table.add_column("ID", style="cyan")
        table.add_column("Type")
        table.add_column("Status", style="green")
        table.add_column("Sequence", style="dim")
        table.add_column("Clip")
        for j in jobs:
            table.add_row(
                j["job_id"][:24],
                j.get("job_type", ""),
                j.get("status", ""),
                j.get("sequence_slug") or "—",
                j.get("clip_id") or "—",
            )
        console.print(table)
        console.print(
            f"[dim]Total: {summary['total']} | "
            f"Refs: {summary['reference_assets']} | "
            f"Queued: {summary['by_status'].get('queued', 0)} | "
            f"Running: {summary['by_status'].get('running', 0)}[/dim]"
        )


    @app.command("cancel")
    def imagine_cancel(
        job_id: str = typer.Argument(...),
        reason: str = typer.Option("", "--reason", "-r"),
    ):
        """Cancel a queued or running job."""
        try:
            job = cancel_job(job_id, reason=reason)
        except KeyError:
            console.print(f"[red]Job not found:[/red] {job_id}")
            raise typer.Exit(1)
        console.print(f"[yellow]Cancelled[/yellow] {job_id} — {job.get('error', '')}")


    @app.command("region")
    def imagine_region(
        set_to: str = typer.Option(None, "--set", help="Region slug"),
        show: bool = typer.Option(False, "--show", help="Show active region and failover chain"),
    ):
        """Configure region-aware Imagine API routing with failover."""
        if set_to:
            try:
                settings = set_imagine_region(set_to)
            except ValueError as exc:
                console.print(f"[red]{exc}[/red]")
                raise typer.Exit(1) from exc
            console.print(f"[green]Region set:[/green] {settings['region']}")
            return
        active = get_active_region()
        chain = get_failover_chain(active)
        table = Table(title="Imagine Regions", box=box.SIMPLE)
        table.add_column("Region", style="cyan")
        table.add_column("Label")
        table.add_column("Active")
        for slug, meta in IMAGINE_REGIONS.items():
            table.add_row(slug, meta["label"], "✓" if slug == active else "")
        console.print(table)
        console.print(f"[dim]Failover chain:[/dim] {' → '.join(chain)}")