#!/usr/bin/env python3
"""Run chain QA gate on a sequence clip."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

from sequence_chain import (  # noqa: E402
    find_sequence,
    get_clip,
    load_sequence,
    run_chain_qa,
    save_sequence,
    update_sequence_health,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run chain QA on a clip")
    parser.add_argument("sequence", help="Sequence name or slug")
    parser.add_argument("--clip", "-c", required=True, help="Clip ID to evaluate")
    parser.add_argument("--scores", "-s", type=str, help="JSON dict of chain QA scores")
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

    clips = seq.get("clips", [])
    idx = clip["index"]
    prev = clips[idx - 1] if idx > 0 else None

    scores = json.loads(args.scores) if args.scores else None
    qa = run_chain_qa(clip, previous_clip=prev, scores=scores)
    clip["chain_qa"] = qa

    if qa["decision"] == "go":
        clip["status"] = "approved"
    elif qa["decision"] == "no_go":
        clip["status"] = "qa_hold"

    update_sequence_health(seq)
    save_sequence(seq)

    print(json.dumps(qa, indent=2))
    print(f"\nDecision: {qa['decision']} | Sequence health: {seq.get('sequence_health_score')}")


if __name__ == "__main__":
    main()