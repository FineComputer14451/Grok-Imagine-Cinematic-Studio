"""Imagine API client and job queue CLI commands."""

from __future__ import annotations

import json

import typer
from rich import box
from rich.markdown import Markdown
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
from artifact_pipeline import artifacts_summary, list_artifacts, register_artifact_from_job
from imagine_bridge import (
    TARGET_SURFACES,
    agent_mode_handoff_to_markdown,
    bridge_to_clipboard,
    bridge_to_markdown,
    build_agent_mode_handoff,
    build_bridge_packet,
)
from production_report import build_production_report, report_to_markdown
from imagine_regions import IMAGINE_REGIONS, get_active_region, get_failover_chain, set_imagine_region
from models import DEFAULT_IMAGINE_IMAGE_MODEL, DEFAULT_IMAGINE_VIDEO_MODEL, verify_model_compatibility
from sequence_chain import get_clip, load_sequence, find_sequence
from sfw_orchestrator import get_next_shots, load_batch as load_sfw_batch

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


    @app.command("verify")
    def imagine_verify():
        """Preflight model stack and Imagine API readiness."""
        check = verify_model_compatibility()
        dry = is_dry_run()
        table = Table(title="Imagine Preflight", box=box.ROUNDED)
        table.add_column("Check", style="cyan")
        table.add_column("Status")
        table.add_row("Model stack", "[green]OK[/green]" if check["compatible"] else "[red]ISSUES[/red]")
        table.add_row("API mode", "[yellow]DRY-RUN[/yellow]" if dry else "[green]LIVE[/green]")
        table.add_row("Active region", get_active_region())
        stack = check.get("model_stack", {})
        table.add_row("Video model", stack.get("imagine_video", "—"))
        table.add_row("Image model", stack.get("imagine_image", "—"))
        console.print(table)
        if not check["compatible"]:
            for issue in check.get("issues", []):
                console.print(f"  [red]•[/red] {issue}")
            raise typer.Exit(1)
        if dry:
            console.print("[dim]Set XAI_API_KEY for live generation.[/dim]")


    @app.command("bridge")
    def imagine_bridge(
        shot_id: str = typer.Option(None, "--shot", help="Batch shot ID"),
        batch: str = typer.Option(None, "--batch", "-b", help="SFW batch slug"),
        sequence: str = typer.Option(None, "--sequence", "-s", help="Sequence slug"),
        clip: str = typer.Option(None, "--clip", "-c", help="Clip ID"),
        format: str = typer.Option("markdown", "--format", "-f", help="markdown | clipboard"),
        output: str = typer.Option(None, "--output", "-o"),
    ):
        """Emit copy-paste-ready grok.com/imagine handoff packet."""
        subject: dict | None = None
        context = "shot"

        if batch and shot_id:
            b = load_sfw_batch(batch)
            for sh in b.get("shots", []):
                if sh["shot_id"] == shot_id:
                    subject = {**sh, "batch_slug": b.get("slug")}
                    break
            if not subject:
                console.print(f"[red]Shot not found in batch:[/red] {shot_id}")
                raise typer.Exit(1)
        elif sequence and clip:
            seq_path = find_sequence(sequence)
            if not seq_path:
                console.print(f"[red]Sequence not found:[/red] {sequence}")
                raise typer.Exit(1)
            seq = load_sequence(seq_path)
            subject = get_clip(seq, clip)
            if not subject:
                console.print(f"[red]Clip not found:[/red] {clip}")
                raise typer.Exit(1)
            subject = {**subject, "sequence_slug": seq.get("slug")}
            context = "clip"
        else:
            console.print("[red]Provide --batch + --shot OR --sequence + --clip[/red]")
            raise typer.Exit(1)

        packet = build_bridge_packet(subject, context=context)
        text = bridge_to_clipboard(packet) if format == "clipboard" else bridge_to_markdown(packet)
        if output:
            from pathlib import Path
            Path(output).write_text(text)
            console.print(f"[green]Bridge written:[/green] {output}")
        else:
            console.print(Panel(text, title=f"Imagine Bridge — {packet['subject_id']}", border_style="cyan"))


    @app.command("agent-handoff")
    def imagine_agent_handoff(
        shot_id: str = typer.Option(None, "--shot", help="Batch shot ID"),
        batch: str = typer.Option(None, "--batch", "-b", help="SFW batch slug"),
        sequence: str = typer.Option(None, "--sequence", "-s", help="Sequence slug"),
        clip: str = typer.Option(None, "--clip", "-c", help="Clip ID"),
        surface: str = typer.Option(
            "grok_build_tools",
            "--surface",
            help="grok_build_tools | grok_agent_acp | grok_com_imagine | xai_api",
        ),
        format: str = typer.Option("markdown", "--format", "-f", help="markdown | json | clipboard"),
        mode: str = typer.Option(None, "--mode", help="Override execution_mode"),
        output: str = typer.Option(None, "--output", "-o"),
    ):
        """Emit official Imagine Agent Mode Handoff packet (protocol v3.7.1)."""
        subject: dict | None = None
        context = "shot"

        if batch and shot_id:
            b = load_sfw_batch(batch)
            for sh in b.get("shots", []):
                if sh["shot_id"] == shot_id:
                    subject = {**sh, "batch_slug": b.get("slug")}
                    break
            if not subject:
                console.print(f"[red]Shot not found in batch:[/red] {shot_id}")
                raise typer.Exit(1)
        elif sequence and clip:
            seq_path = find_sequence(sequence)
            if not seq_path:
                console.print(f"[red]Sequence not found:[/red] {sequence}")
                raise typer.Exit(1)
            seq = load_sequence(seq_path)
            subject = get_clip(seq, clip)
            if not subject:
                console.print(f"[red]Clip not found:[/red] {clip}")
                raise typer.Exit(1)
            subject = {**subject, "sequence_slug": seq.get("slug")}
            context = "clip"
        else:
            console.print("[red]Provide --batch + --shot OR --sequence + --clip[/red]")
            raise typer.Exit(1)

        if surface not in TARGET_SURFACES:
            console.print(
                f"[red]Invalid --surface:[/red] {surface}\n"
                f"Expected one of: {', '.join(sorted(TARGET_SURFACES))}"
            )
            raise typer.Exit(1)

        try:
            packet = build_agent_mode_handoff(
                subject,
                target_surface=surface,
                context=context,
                execution_mode=mode,
            )
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc

        if format == "json":
            text = json.dumps(packet, indent=2)
        elif format == "clipboard":
            # Web-ready single block when surface is grok.com; else markdown
            if surface == "grok_com_imagine":
                text = bridge_to_clipboard(build_bridge_packet(subject, context=context))
            else:
                text = agent_mode_handoff_to_markdown(packet)
        else:
            text = agent_mode_handoff_to_markdown(packet)

        if output:
            from pathlib import Path

            Path(output).write_text(text)
            console.print(f"[green]Agent-mode handoff written:[/green] {output}")
        else:
            console.print(
                Panel(
                    text if format != "json" else Markdown(f"```json\n{text}\n```"),
                    title=f"Imagine Agent Mode Handoff — {packet['subject_id']}",
                    border_style="magenta",
                )
            )


    @app.command("workflow")
    def imagine_workflow(
        batch: str = typer.Option(None, "--batch", "-b"),
        sequence: str = typer.Option(None, "--sequence", "-s"),
        shot_id: str = typer.Option(None, "--shot"),
        clip: str = typer.Option(None, "--clip", "-c"),
        dry_run: bool = typer.Option(False, "--dry-run"),
        count: int = typer.Option(1, "--count", "-n", help="Next shots to show when no --shot"),
    ):
        """Preflight → plan queue → generate hint → QA record loop."""
        check = verify_model_compatibility()
        if not check["compatible"]:
            console.print("[red]Model stack incompatible — run: models verify[/red]")
            raise typer.Exit(1)

        mode_label = "[yellow]DRY-RUN[/yellow]" if (dry_run or is_dry_run()) else "[green]LIVE[/green]"
        console.print(Panel(f"Imagine workflow ready · {mode_label}", border_style="cyan"))

        if batch:
            try:
                b = load_sfw_batch(batch)
            except FileNotFoundError:
                console.print(f"[red]Batch not found:[/red] {batch}")
                raise typer.Exit(1)
            if shot_id:
                console.print(f"[bold]Target shot:[/bold] {shot_id}")
                console.print("[dim]Run: sfw run {batch} {shot_id}{dry}".format(
                    batch=batch, shot_id=shot_id, dry=" --dry-run" if dry_run else "",
                ))
            else:
                shots = get_next_shots(b, count=count)
                if not shots:
                    console.print("[yellow]No pending shots.[/yellow]")
                    return
                table = Table(title=f"Next — {b['title']}", box=box.SIMPLE)
                table.add_column("Shot", style="cyan")
                table.add_column("Mode")
                table.add_column("Models", style="dim")
                table.add_column("Est. cr", justify="right")
                for sh in shots:
                    table.add_row(
                        sh["shot_id"],
                        sh.get("decision", {}).get("mode", sh.get("recommended_mode", "")),
                        f"{sh.get('image_model')} → {sh.get('video_model')}",
                        str(sh.get("cost_estimate", {}).get("credits", "?")),
                    )
                console.print(table)
                console.print(f"[dim]Run: sfw run {batch} {shots[0]['shot_id']}{' --dry-run' if dry_run else ''}[/dim]")
                console.print(f"[dim]QA: sfw record {batch} {shots[0]['shot_id']} --score 8 --credits 10[/dim]")
            console.print(f"[dim]Bridge: imagine bridge --batch {batch} --shot <id>[/dim]")
        elif sequence and clip:
            console.print(f"[dim]Run: sequence run {sequence} --clip {clip}{' --dry-run' if dry_run else ''}[/dim]")
            console.print(f"[dim]Bridge: imagine bridge --sequence {sequence} --clip {clip}[/dim]")
        else:
            console.print("[red]Provide --batch or --sequence + --clip[/red]")
            raise typer.Exit(1)


    @app.command("artifact")
    def imagine_artifact(
        job_id: str = typer.Argument(..., help="Imagine job ID"),
        download: bool = typer.Option(False, "--download", help="Attempt URL download"),
    ):
        """Register job output in artifact pipeline."""
        try:
            entry = register_artifact_from_job(job_id, download=download)
        except (KeyError, ValueError) as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        console.print(Panel(
            f"Job: {entry['job_id']}\n"
            f"URL: {entry['result_url']}\n"
            f"Manifest: {entry['local_path']}.manifest.json\n"
            f"Downloaded: {entry.get('downloaded', False)}",
            title="Artifact Registered",
            border_style="green",
        ))


    @app.command("artifacts")
    def imagine_artifacts(
        limit: int = typer.Option(15, "--limit", "-n"),
    ):
        """List registered generation artifacts."""
        summary = artifacts_summary()
        entries = list_artifacts(limit=limit)
        table = Table(title="Generation Artifacts", box=box.SIMPLE)
        table.add_column("Shot/Clip", style="cyan")
        table.add_column("Pipeline")
        table.add_column("Downloaded")
        table.add_column("Path", style="dim")
        for e in entries:
            table.add_row(
                e.get("shot_id") or e.get("clip_id") or "—",
                e.get("pipeline") or "—",
                str(e.get("downloaded", False)),
                (e.get("local_path") or "")[-40:],
            )
        console.print(table)
        console.print(f"[dim]Total: {summary['total']} · Downloaded: {summary['downloaded']}[/dim]")


    @app.command("report")
    def imagine_report(
        output: str = typer.Option(None, "--output", "-o"),
    ):
        """Unified production report (quota, batches, jobs, artifacts)."""
        report = build_production_report()
        md = report_to_markdown(report)
        if output:
            from pathlib import Path
            Path(output).write_text(md)
            console.print(f"[green]Report written:[/green] {output}")
        else:
            console.print(Markdown(md))