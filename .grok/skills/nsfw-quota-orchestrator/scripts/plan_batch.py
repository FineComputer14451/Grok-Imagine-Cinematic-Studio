#!/usr/bin/env python3
"""Thin wrapper — plan NSFW batch from JSON shot list."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

from nsfw_orchestrator import batch_to_markdown, plan_batch, save_batch  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan NSFW production batch")
    parser.add_argument("title", help="Batch title")
    parser.add_argument("--file", "-f", required=True, help="JSON shot list")
    parser.add_argument("--budget", "-b", type=float, default=None)
    parser.add_argument("--tier", default="supergrok_heavy")
    parser.add_argument("--fast-mode", action="store_true")
    parser.add_argument("--output", "-o", help="Write markdown plan to file")
    args = parser.parse_args()

    shots = json.loads(Path(args.file).read_text())
    batch = plan_batch(args.title, shots, tier=args.tier, budget_credits=args.budget, fast_mode=args.fast_mode)
    path = save_batch(batch)
    md = batch_to_markdown(batch)

    print(f"Saved: {path}")
    print(f"Scheduled: {batch['shots_scheduled']}/{batch['shots_total']} shots ({batch['scheduled_credits']} credits)")
    if args.output:
        Path(args.output).write_text(md)
        print(f"Plan: {args.output}")
    else:
        print(md)


if __name__ == "__main__":
    main()