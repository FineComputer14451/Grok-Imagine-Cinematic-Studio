#!/usr/bin/env python3
"""Build Grok Imagine Video 1.5 extend prompt for the next clip."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

from sequence_chain import build_extend_prompt, find_sequence, get_clip, load_sequence  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Build 1.5 extend prompt")
    parser.add_argument("sequence", help="Sequence name or slug")
    parser.add_argument("--clip", "-c", required=True, help="Previous clip ID")
    parser.add_argument("--beat", "-b", required=True, help="Next narrative beat")
    parser.add_argument("--character", help="Optional CHARACTER_DNA injection block")
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

    print(build_extend_prompt(seq, clip, args.beat, character_injection=args.character or ""))


if __name__ == "__main__":
    main()