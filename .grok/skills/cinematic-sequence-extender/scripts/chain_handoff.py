#!/usr/bin/env python3
"""Generate extend/stitch handoff packet from a sequence clip."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

from sequence_chain import build_handoff_from_clip, find_sequence, get_clip, load_sequence  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sequence extend handoff packet")
    parser.add_argument("sequence", help="Sequence name or slug")
    parser.add_argument("--clip", "-c", required=True, help="Source clip ID")
    parser.add_argument("--output", "-o", type=Path, help="Output path")
    args = parser.parse_args()

    seq_path = find_sequence(args.sequence)
    if not seq_path:
        print(f"ERROR: Sequence not found: {args.sequence}", file=sys.stderr)
        sys.exit(1)

    seq = load_sequence(seq_path)
    clip = get_clip(seq, args.clip)
    if not clip:
        print(f"ERROR: Clip not found: {args.clip}", file=sys.stderr)
        sys.exit(1)

    handoff = build_handoff_from_clip(clip)
    out = args.output or seq_path.parent / f"handoff_{args.clip}.json"
    out.write_text(json.dumps(handoff, indent=2))
    print(f"Handoff written: {out}")
    print(f"Transition: {handoff['transition_recommendation']}")


if __name__ == "__main__":
    main()