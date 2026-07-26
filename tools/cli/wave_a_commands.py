"""Wave A CLI — build/validate specialist packets and spend gates."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import typer

from wave_a_packets import (
    attach_wave_a_to_imagine,
    build_brief_dispatch_log,
    build_contact_brief,
    build_crop_plan,
    build_dialogue_block,
    build_hmu_lock,
    build_plate_motion_readiness,
    build_score_block,
    build_title_brief,
    validate_optional_wave_a_fields,
)

from cli.shared import console

# Resolve handoff validator next to skills
_REPO = Path(__file__).resolve().parents[2]
_VALIDATOR = (
    _REPO
    / ".grok"
    / "skills"
    / "handoff-packet-validator"
    / "scripts"
    / "validate_handoff.py"
)


def _write_json(path: Path | None, data: dict[str, Any], *, default_name: str) -> Path:
    if path is None:
        out_dir = _REPO / "artifacts" / "handoffs"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / default_name
    else:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def _print_packet(data: dict[str, Any], path: Path) -> None:
    console.print_json(data=data)
    console.print(f"[green]Wrote[/green] {path}")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        console.print(f"[red]File not found:[/red] {path}")
        raise typer.Exit(1)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid JSON:[/red] {exc}")
        raise typer.Exit(1) from exc
    if not isinstance(data, dict):
        console.print("[red]Root must be a JSON object[/red]")
        raise typer.Exit(1)
    return data


def _run_validator(path: Path, *, strict_wave_a: bool = False) -> int:
    if not _VALIDATOR.is_file():
        console.print(f"[red]Validator not found:[/red] {_VALIDATOR}")
        raise typer.Exit(2)
    import subprocess

    cmd = [sys.executable, str(_VALIDATOR), str(path)]
    if strict_wave_a:
        cmd.append("--strict-wave-a")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.stdout:
        console.print(proc.stdout.rstrip())
    if proc.stderr:
        console.print(proc.stderr.rstrip())
    return int(proc.returncode)


def _build(fn, **kwargs: Any) -> dict[str, Any]:
    """Run a Wave A builder; map ValueError/TypeError to CLI exit 2."""
    try:
        return fn(**kwargs)
    except (TypeError, ValueError) as exc:
        console.print(f"[red]Build rejected:[/red] {exc}")
        raise typer.Exit(2) from exc


def _emit_built(
    pkt: dict[str, Any],
    *,
    output: Path | None,
    default_name: str,
    validate: bool = True,
) -> Path:
    """Write + print + optional validate — shared by all builder commands."""
    out = _write_json(output, pkt, default_name=default_name)
    _print_packet(pkt, out)
    if validate and _run_validator(out) != 0:
        raise typer.Exit(1)
    return out


def register(app: typer.Typer) -> None:
    wave = typer.Typer(
        help="Wave A specialist packets (plate/motion, HMU, dialogue, score, titles, crops, briefs)"
    )
    app.add_typer(wave, name="wave-a")

    @wave.command("plate-motion")
    def plate_motion(
        subject_id: str = typer.Argument(..., help="Shot / subject id"),
        status: str = typer.Option(..., "--status", help="draft | approved | locked"),
        action: str = typer.Option(..., "--action", help="motion_vector.action"),
        camera: str = typer.Option(..., "--camera", help="motion_vector.camera"),
        emotion: str = typer.Option(..., "--emotion", help="motion_vector.emotion"),
        ready: bool = typer.Option(True, "--ready/--not-ready", help="i2v_motion_block_ready"),
        path: str = typer.Option(None, "--path", help="plate_path"),
        asset_id: str = typer.Option(None, "--asset-id", help="plate_asset_id"),
        output: Path = typer.Option(None, "--output", "-o", help="Write JSON path"),
        validate: bool = typer.Option(True, "--validate/--no-validate"),
    ):
        """Build plate_motion_readiness packet."""
        _emit_built(
            _build(
                build_plate_motion_readiness,
                subject_id=subject_id,
                plate_status=status,
                action=action,
                camera=camera,
                emotion=emotion,
                i2v_motion_block_ready=ready,
                plate_path=path,
                plate_asset_id=asset_id,
            ),
            output=output,
            default_name=f"plate_motion_{subject_id}.json",
            validate=validate,
        )

    @wave.command("contact")
    def contact(
        subject_id: str = typer.Argument(...),
        brief: str = typer.Option(..., "--brief", "-b", help="Contact brief sentence"),
        hands: str = typer.Option("", "--hands"),
        cloth: str = typer.Option("", "--cloth"),
        weight: str = typer.Option("", "--weight", help="weight_transfer"),
        liquids: str = typer.Option("", "--liquids"),
        output: Path = typer.Option(None, "--output", "-o"),
        validate: bool = typer.Option(True, "--validate/--no-validate"),
    ):
        """Build contact_micro_physics_brief packet."""
        _emit_built(
            _build(
                build_contact_brief,
                subject_id=subject_id,
                contact_brief=brief,
                hands=hands,
                cloth=cloth,
                weight_transfer=weight,
                liquids=liquids,
            ),
            output=output,
            default_name=f"contact_{subject_id}.json",
            validate=validate,
        )

    @wave.command("hmu")
    def hmu(
        character_slug: str = typer.Argument(...),
        look_id: str = typer.Option(..., "--look-id", help="active_look_id"),
        hair: str = typer.Option(..., "--hair"),
        makeup: str = typer.Option(..., "--makeup"),
        condition: str = typer.Option("clean", "--condition"),
        inject: str = typer.Option("", "--inject", help="inject_compact"),
        output: Path = typer.Option(None, "--output", "-o"),
        validate: bool = typer.Option(True, "--validate/--no-validate"),
    ):
        """Build hmu_lock_handoff packet."""
        _emit_built(
            _build(
                build_hmu_lock,
                character_slug=character_slug,
                active_look_id=look_id,
                hair=hair,
                makeup=makeup,
                condition=condition,
                inject_compact=inject,
            ),
            output=output,
            default_name=f"hmu_{character_slug}.json",
            validate=validate,
        )

    @wave.command("dialogue")
    def dialogue(
        subject_id: str = typer.Argument(...),
        line: list[str] = typer.Option(None, "--line", "-l", help="Dialogue line (repeatable)"),
        vo: str = typer.Option("", "--vo"),
        adr: str = typer.Option("", "--adr", help="ADR notes"),
        lip_sync: str = typer.Option("", "--lip-sync"),
        seed: str = typer.Option("", "--seed", help="native_dialogue_seed"),
        output: Path = typer.Option(None, "--output", "-o"),
        validate: bool = typer.Option(True, "--validate/--no-validate"),
    ):
        """Build dialogue_adr_block packet."""
        _emit_built(
            build_dialogue_block(
                subject_id=subject_id,
                lines=list(line or []),
                vo=vo,
                adr_notes=adr,
                lip_sync_cues=lip_sync,
                native_dialogue_seed=seed,
            ),
            output=output,
            default_name=f"dialogue_{subject_id}.json",
            validate=validate,
        )

    @wave.command("score")
    def score(
        subject_id: str = typer.Argument(...),
        cue: list[str] = typer.Option(None, "--cue", "-c", help="Music cue (repeatable)"),
        temp_notes: str = typer.Option("", "--temp-notes"),
        tone: str = typer.Option("", "--tone", help="emotional_tone_audio"),
        output: Path = typer.Option(None, "--output", "-o"),
        validate: bool = typer.Option(True, "--validate/--no-validate"),
    ):
        """Build score_temp_music_block packet."""
        _emit_built(
            build_score_block(
                subject_id=subject_id,
                music_cues=list(cue or []),
                temp_score_notes=temp_notes,
                emotional_tone_audio=tone,
            ),
            output=output,
            default_name=f"score_{subject_id}.json",
            validate=validate,
        )

    @wave.command("title")
    def title(
        deliverable_id: str = typer.Argument(...),
        text: str = typer.Option(..., "--text", "-t", help="Primary title card text"),
        placement: str = typer.Option("center", "--placement"),
        output: Path = typer.Option(None, "--output", "-o"),
        validate: bool = typer.Option(True, "--validate/--no-validate"),
    ):
        """Build title_mograph_brief packet."""
        _emit_built(
            build_title_brief(
                deliverable_id=deliverable_id,
                title_cards=[{"text": text, "placement": placement}],
            ),
            output=output,
            default_name=f"title_{deliverable_id}.json",
            validate=validate,
        )

    @wave.command("crop")
    def crop(
        subject_id: str = typer.Argument(...),
        safe_action: str = typer.Option(
            "protect hero face/torso", "--safe-action", help="Safe-action note"
        ),
        output: Path = typer.Option(None, "--output", "-o"),
        validate: bool = typer.Option(True, "--validate/--no-validate"),
    ):
        """Build distribution_crop_plan packet (default 16:9 / 9:16 / 1:1)."""
        _emit_built(
            build_crop_plan(subject_id=subject_id, safe_action=safe_action),
            output=output,
            default_name=f"crop_{subject_id}.json",
            validate=validate,
        )

    @wave.command("briefs")
    def briefs(
        session_id: str = typer.Argument(...),
        to: str = typer.Option(
            "plate-motion-readiness-lead",
            "--to",
            help="Specialist skill slug for sample brief",
        ),
        scope: str = typer.Option("lock plate + motion", "--scope"),
        priority: str = typer.Option("high", "--priority"),
        output: Path = typer.Option(None, "--output", "-o"),
        validate: bool = typer.Option(True, "--validate/--no-validate"),
    ):
        """Build parallel_brief_dispatch_log packet (starter entry)."""
        _emit_built(
            build_brief_dispatch_log(
                session_id=session_id,
                briefs=[
                    {
                        "brief_id": f"pb-{session_id}-001",
                        "to": to,
                        "priority": priority,
                        "scope": scope,
                    }
                ],
            ),
            output=output,
            default_name=f"briefs_{session_id}.json",
            validate=validate,
        )

    @wave.command("validate")
    def validate_cmd(
        path: Path = typer.Argument(..., help="Handoff / Wave A packet JSON"),
        strict_wave_a: bool = typer.Option(
            False,
            "--strict-wave-a",
            help="Still→video requires locked plate + complete motion triple",
        ),
    ):
        """Validate a packet via handoff-packet-validator (Wave A aware)."""
        code = _run_validator(path, strict_wave_a=strict_wave_a)
        raise typer.Exit(code)

    @wave.command("attach")
    def attach(
        imagine_packet: Path = typer.Argument(..., help="imagine_agent_mode_handoff JSON"),
        plate_motion: Path = typer.Option(None, "--plate-motion", help="plate_motion_readiness JSON"),
        contact: Path = typer.Option(None, "--contact"),
        hmu: Path = typer.Option(None, "--hmu"),
        dialogue: Path = typer.Option(None, "--dialogue"),
        score: Path = typer.Option(None, "--score"),
        title: Path = typer.Option(None, "--title"),
        crop: Path = typer.Option(None, "--crop"),
        output: Path = typer.Option(None, "--output", "-o"),
        strict_wave_a: bool = typer.Option(False, "--strict-wave-a"),
    ):
        """Merge Wave A packets onto an imagine_agent_mode_handoff JSON."""
        base = _load_json(imagine_packet)
        kwargs: dict[str, Any] = {}
        if plate_motion:
            kwargs["plate_motion"] = _load_json(plate_motion)
        if contact:
            kwargs["contact"] = _load_json(contact)
        if hmu:
            kwargs["hmu"] = _load_json(hmu)
        if dialogue:
            kwargs["dialogue"] = _load_json(dialogue)
        if score:
            kwargs["score"] = _load_json(score)
        if title:
            kwargs["title"] = _load_json(title)
        if crop:
            kwargs["crop"] = _load_json(crop)
        if not kwargs:
            console.print("[red]Provide at least one Wave A packet path to attach[/red]")
            raise typer.Exit(2)
        try:
            merged = attach_wave_a_to_imagine(base, **kwargs)
        except (TypeError, ValueError) as exc:
            console.print(f"[red]Attach rejected:[/red] {exc}")
            raise typer.Exit(2) from exc
        out = _write_json(
            output,
            merged,
            default_name=f"imagine_wave_a_{merged.get('subject_id', 'packet')}.json",
        )
        _print_packet(merged, out)
        issues, warnings = validate_optional_wave_a_fields(merged)
        for w in warnings:
            console.print(f"[yellow]⚠️  {w}[/yellow]")
        if issues:
            for i in issues:
                console.print(f"[red]{i}[/red]")
            raise typer.Exit(1)
        if strict_wave_a and _run_validator(out, strict_wave_a=True) != 0:
            raise typer.Exit(1)
