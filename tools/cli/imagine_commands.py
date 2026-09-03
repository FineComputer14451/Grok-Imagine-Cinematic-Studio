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
    submit_video_edit,
    submit_video_extension,
    submit_video_generation,
)
from imagine_jobs import cancel_job, create_job, get_job, job_summary, list_jobs, transition_job
from artifact_pipeline import artifacts_summary, list_artifacts, register_artifact_from_job
from imagine_bridge import (
    TARGET_SURFACES,
    build_agent_mode_handoff,
    build_bridge_packet,
    handoff_to_clipboard,
    handoff_to_markdown,
)
from production_report import build_production_report, report_to_markdown
from imagine_regions import IMAGINE_REGIONS, get_active_region, get_failover_chain, set_imagine_region
from models import (
    DEFAULT_IMAGINE_IMAGE_MODEL,
    DEFAULT_IMAGINE_VIDEO_MODEL,
    EDIT_EXTEND_VIDEO_MODEL,
    HERO_IMAGINE_IMAGE_MODEL,
    imagine_surface_catalog,
    resolve_image_request,
    verify_model_compatibility,
)
from sequence_chain import get_clip, load_sequence, find_sequence
from sfw_orchestrator import get_next_shots, load_batch as load_sfw_batch

from cli.shared import console


def resolve_handoff_subject(
    *,
    batch: str | None = None,
    shot_id: str | None = None,
    sequence: str | None = None,
    clip: str | None = None,
) -> tuple[dict, str]:
    """
    Resolve batch shot or sequence clip into (subject, context).

    Raises ValueError with a user-facing message on failure.
    """
    if batch and shot_id:
        b = load_sfw_batch(batch)
        for sh in b.get("shots", []):
            if sh["shot_id"] == shot_id:
                return {**sh, "batch_slug": b.get("slug")}, "shot"
        raise ValueError(f"Shot not found in batch: {shot_id}")
    if sequence and clip:
        seq_path = find_sequence(sequence)
        if not seq_path:
            raise ValueError(f"Sequence not found: {sequence}")
        seq = load_sequence(seq_path)
        subject = get_clip(seq, clip)
        if not subject:
            raise ValueError(f"Clip not found: {clip}")
        return {**subject, "sequence_slug": seq.get("slug")}, "clip"
    raise ValueError("Provide --batch + --shot OR --sequence + --clip")


def register(app: typer.Typer) -> None:
    @app.command("submit")
    def imagine_submit(
        job_type: str = typer.Argument(
            ...,
            help="image | image_edit | video | video_edit | video_extend | reference_to_video",
        ),
        prompt: str = typer.Option(..., "--prompt", "-p"),
        model: str = typer.Option(None, "--model", "-m"),
        image_url: str = typer.Option(None, "--image-url", help="Source image for edit or i2v"),
        video_url: str = typer.Option(None, "--video-url", help="Source video for edit or extend"),
        file_id: str = typer.Option(None, "--file-id", help="Files API file_id for image or video input"),
        reference_image_url: list[str] = typer.Option(
            None,
            "--reference-image-url",
            help="Repeatable r2v ref URL; also extra stills for image_edit (prefer --extra-image-url)",
        ),
        extra_image_url: list[str] = typer.Option(
            None,
            "--extra-image-url",
            help="Repeatable extra still URL for image_edit (Image 2.0: up to 5 total)",
        ),
        voice_id: list[str] = typer.Option(
            None,
            "--voice-id",
            help="Repeatable preset voice_id for r2v (Video 1.5)",
        ),
        duration: int = typer.Option(10, "--duration", "-d", help="Video duration seconds"),
        resolution: str = typer.Option(None, "--resolution", help="1k|2k for images; 480p|720p|1080p for video"),
        quality: str = typer.Option(
            None, "--quality", help="Image 2.0 quality: low | medium | auto"
        ),
        aspect_ratio: str = typer.Option(
            None, "--aspect-ratio", help="e.g. 16:9, 21:9, 5:2"
        ),
        sequence: str = typer.Option(None, "--sequence", help="Link to sequence slug"),
        clip: str = typer.Option(None, "--clip", help="Link to clip ID"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Force mock response"),
    ):
        """Submit an Imagine generation job and track it in the job queue."""
        allowed = ("image", "image_edit", "video", "video_edit", "video_extend", "reference_to_video")
        if job_type not in allowed:
            console.print(f"[red]job_type must be one of: {', '.join(allowed)}[/red]")
            raise typer.Exit(1)

        refs = list(reference_image_url or [])
        voices = list(voice_id or [])
        if job_type == "image_edit":
            img_model = model or HERO_IMAGINE_IMAGE_MODEL
        else:
            img_model = model or DEFAULT_IMAGINE_IMAGE_MODEL
        vid_model = model or DEFAULT_IMAGINE_VIDEO_MODEL
        if job_type in ("video_edit", "video_extend"):
            vid_model = model or EDIT_EXTEND_VIDEO_MODEL
        quality_sent = quality
        if job_type in ("image", "image_edit"):
            img_mode = "edit" if job_type == "image_edit" else "generate"
            try:
                img_model, quality_sent, img_warnings = resolve_image_request(
                    img_model, quality=quality, mode=img_mode
                )
            except ValueError as exc:
                console.print(f"[red]{exc}[/red]")
                raise typer.Exit(1) from exc
            for warning in img_warnings:
                console.print(f"[yellow]{warning}[/yellow]")
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
            request_id = None
            if job_type == "image":
                resp = generate_image(
                    prompt,
                    model=img_model,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution,
                    quality=quality_sent,
                    dry_run=force_dry,
                )
                url = extract_image_url(resp)
                transition_job(job["job_id"], "approved", result_url=url)
            elif job_type == "image_edit":
                if not image_url and not file_id:
                    console.print("[red]--image-url or --file-id required for image_edit[/red]")
                    raise typer.Exit(1)
                extras = list(
                    dict.fromkeys([*(extra_image_url or []), *refs])
                )
                resp = edit_image(
                    prompt,
                    image_url=image_url,
                    image_file_id=file_id,
                    extra_image_urls=extras,
                    model=img_model,
                    quality=quality_sent,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution,
                    dry_run=force_dry,
                )
                url = extract_image_url(resp)
                transition_job(job["job_id"], "approved", result_url=url)
            elif job_type == "video_edit":
                if not video_url and not file_id:
                    console.print("[red]--video-url or --file-id required for video_edit[/red]")
                    raise typer.Exit(1)
                resp = submit_video_edit(
                    prompt,
                    video_url=video_url,
                    video_file_id=file_id,
                    model=vid_model,
                    dry_run=force_dry,
                )
                request_id = resp.get("request_id")
                url = extract_video_url(resp)
                if resp.get("status") != "done" and not force_dry:
                    result = poll_video_job(request_id)
                    url = extract_video_url(result)
                transition_job(job["job_id"], "qa_pending", request_id=request_id, result_url=url)
            elif job_type == "video_extend":
                if not video_url and not file_id:
                    console.print("[red]--video-url or --file-id required for video_extend[/red]")
                    raise typer.Exit(1)
                resp = submit_video_extension(
                    prompt,
                    video_url=video_url,
                    video_file_id=file_id,
                    model=vid_model,
                    duration=duration,
                    dry_run=force_dry,
                )
                request_id = resp.get("request_id")
                url = extract_video_url(resp)
                if resp.get("status") != "done" and not force_dry:
                    result = poll_video_job(request_id)
                    url = extract_video_url(result)
                transition_job(job["job_id"], "qa_pending", request_id=request_id, result_url=url)
            else:
                # video (t2v/i2v) or reference_to_video
                resp = submit_video_generation(
                    prompt,
                    model=vid_model,
                    duration=duration,
                    image_url=image_url,
                    image_file_id=file_id if job_type != "reference_to_video" else None,
                    reference_image_urls=refs,
                    reference_audios=voices,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution,
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
            served = None
            if job_type in ("image", "image_edit"):
                served = resp.get("model")
            model_line = f"Model: {slug}"
            if served and served != slug:
                model_line += f"\nServed: {served}"
            console.print(Panel(
                f"Job: {job['job_id']}\n"
                f"Type: {job_type}\n"
                f"Mode: {mode}\n"
                f"{model_line}\n"
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
        table.add_row("Hero stills", HERO_IMAGINE_IMAGE_MODEL)
        console.print(table)
        catalog = imagine_surface_catalog()
        surf = Table(title="Agent Mode surfaces", box=box.SIMPLE)
        surf.add_column("ID", style="cyan")
        surf.add_column("Surface")
        for row in catalog.get("agent_mode_surfaces", []):
            surf.add_row(row.get("id", ""), f"{row.get('letter', '')}. {row.get('label', '')}")
        console.print(surf)
        if not check["compatible"]:
            for issue in check.get("issues", []):
                console.print(f"  [red]•[/red] {issue}")
            raise typer.Exit(1)
        if dry:
            console.print("[dim]Set XAI_API_KEY for live generation.[/dim]")
        console.print("[dim]No grok-imagine-video-2.0 — 2.0 is Imagine Image only.[/dim]")


    def _write_handoff_output(
        packet: dict,
        text: str,
        *,
        title: str,
        border: str,
        output: str | None,
        as_json: bool = False,
    ) -> None:
        if output:
            from pathlib import Path

            Path(output).write_text(text)
            console.print(f"[green]Handoff written:[/green] {output}")
            return
        body = Markdown(f"```json\n{text}\n```") if as_json else text
        console.print(Panel(body, title=title, border_style=border))

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
        try:
            subject, context = resolve_handoff_subject(
                batch=batch, shot_id=shot_id, sequence=sequence, clip=clip
            )
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc

        packet = build_bridge_packet(subject, context=context)
        text = (
            handoff_to_clipboard(packet)
            if format == "clipboard"
            else handoff_to_markdown(packet)
        )
        _write_handoff_output(
            packet,
            text,
            title=f"Imagine Bridge — {packet['subject_id']}",
            border="cyan",
            output=output,
        )

    @app.command("agent-handoff")
    def imagine_agent_handoff(
        shot_id: str = typer.Option(None, "--shot", help="Batch shot ID"),
        batch: str = typer.Option(None, "--batch", "-b", help="SFW batch slug"),
        sequence: str = typer.Option(None, "--sequence", "-s", help="Sequence slug"),
        clip: str = typer.Option(None, "--clip", "-c", help="Clip ID"),
        surface: str = typer.Option(
            "grok_build_tools",
            "--surface",
            help="grok_build_tools | grok_agent_acp | grok_com_imagine | xai_api | xai_responses_tool",
        ),
        format: str = typer.Option("markdown", "--format", "-f", help="markdown | json | clipboard"),
        mode: str = typer.Option(None, "--mode", help="Override execution_mode"),
        output: str = typer.Option(None, "--output", "-o"),
        strict_handoff: bool = typer.Option(
            False,
            "--strict-handoff",
            help="Exit 1 if semantic readiness fails (blockers); do not write output",
        ),
        strict_wave_a: bool = typer.Option(
            False,
            "--strict-wave-a",
            help=(
                "Wave A still→video gates (plate approved/locked + motion triple); "
                "implies readiness hard-fail like --strict-handoff for motion"
            ),
        ),
        checklist: str = typer.Option(
            None,
            "--checklist",
            help=(
                "Specialist order confirmations, e.g. "
                "dna,lock,curator,prompt,i2v or dna=1,lock=true"
            ),
        ),
    ):
        """Emit official Imagine Agent Mode Handoff packet (protocol v3.7.1)."""
        from handoff_readiness import evaluate_imagine_handoff_readiness
        from specialist_order import parse_checklist_csv
        from wave_a_packets import validate_optional_wave_a_fields

        try:
            subject, context = resolve_handoff_subject(
                batch=batch, shot_id=shot_id, sequence=sequence, clip=clip
            )
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc

        if surface not in TARGET_SURFACES:
            console.print(
                f"[red]Invalid --surface:[/red] {surface}\n"
                f"Expected one of: {', '.join(sorted(TARGET_SURFACES))}"
            )
            raise typer.Exit(1)

        state = None
        if checklist:
            state = {"specialist_checklist": parse_checklist_csv(checklist)}

        try:
            packet = build_agent_mode_handoff(
                subject,
                target_surface=surface,
                context=context,
                execution_mode=mode,
                state=state,
            )
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc

        # --strict-handoff / --strict-wave-a require complete motion_vector triple (MB-02)
        hard = strict_handoff or strict_wave_a
        ready = evaluate_imagine_handoff_readiness(
            packet, strict_motion=hard
        )
        for w in ready.get("warnings") or []:
            console.print(f"[yellow]⚠️  {w}[/yellow]")
        if ready.get("blockers"):
            for b in ready["blockers"]:
                console.print(f"[yellow]⚠️  readiness blocker: {b}[/yellow]")
            if ready.get("fixes"):
                console.print("[dim]Fixes:[/dim]")
                for fix in ready["fixes"]:
                    console.print(f"  → {fix}")
        # Wave A shape issues always hard-fail (same as handoff-packet-validator).
        # Plate/motion readiness hard-fail only under --strict-handoff / --strict-wave-a.
        wa_issues, wa_warnings = validate_optional_wave_a_fields(packet)
        for w in wa_warnings:
            console.print(f"[yellow]⚠️  wave-a: {w}[/yellow]")
        if wa_issues:
            for i in wa_issues:
                console.print(f"[red]wave-a: {i}[/red]")
            console.print("[red]Wave A field checks failed[/red]")
            raise typer.Exit(1)
        if hard and not ready.get("pass"):
            flag = "--strict-wave-a" if strict_wave_a else "--strict-handoff"
            console.print(f"[red]Handoff readiness failed ({flag})[/red]")
            raise typer.Exit(1)

        if format == "json":
            text = json.dumps(packet, indent=2)
        elif format == "clipboard":
            # Always serialize the official packet (no second rebuild)
            text = handoff_to_clipboard(packet)
        else:
            text = handoff_to_markdown(packet)

        _write_handoff_output(
            packet,
            text,
            title=f"Imagine Agent Mode Handoff — {packet['subject_id']}",
            border="magenta",
            output=output,
            as_json=(format == "json"),
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