#!/usr/bin/env python3
"""Plan NSFW sequence extension from reference frame or short clip."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

from aup_gate import AUPGateError  # noqa: E402
from nsfw_sequence_extender import (  # noqa: E402
    nsfw_sequence_to_markdown,
    plan_nsfw_extension,
    save_nsfw_sequence,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan NSFW sensual sequence extension")
    parser.add_argument("title", help="Sequence title")
    parser.add_argument("--duration", "-d", type=int, default=90)
    parser.add_argument("--profile", default="passionate", choices=["slow_burn", "passionate", "intense"])
    parser.add_argument(
        "--source",
        default="short_clip",
        choices=["reference_frame", "short_clip"],
        help="short_clip (default). reference_frame is blocked for intimate stills (AUP).",
    )
    parser.add_argument("--reference", "-r", default="", help="Reference frame or clip description")
    parser.add_argument("--beat", "-b", action="append", help="Custom beat override")
    parser.add_argument("--output", "-o", help="Write markdown plan to file")
    args = parser.parse_args()

    try:
        seq = plan_nsfw_extension(
            args.title,
            target_duration=args.duration,
            source_type=args.source,
            reference_description=args.reference,
            tension_profile=args.profile,
            custom_beats=args.beat,
        )
    except AUPGateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    path = save_nsfw_sequence(seq)
    md = nsfw_sequence_to_markdown(seq)

    est = seq.get("cost_estimate", {})
    print(f"Saved: {path}")
    print(f"Clips: {len(seq.get('clips', []))} | Credits: {est.get('credits_low', '?')}–{est.get('credits_high', '?')}")
    if args.output:
        Path(args.output).write_text(md)
        print(f"Plan: {args.output}")
    else:
        print(md)


if __name__ == "__main__":
    main()