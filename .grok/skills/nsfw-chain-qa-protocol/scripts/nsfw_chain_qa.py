#!/usr/bin/env python3
"""Run NSFW chain QA gate on an intimate sequence clip."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

from nsfw_sequence_extender import (  # noqa: E402
    evaluate_nsfw_chain_qa,
    run_nsfw_chain_qa_scaffold,
    save_nsfw_sequence,
)
from sequence_chain import find_sequence, get_clip, load_sequence  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run NSFW chain QA on a clip")
    parser.add_argument("sequence", help="Sequence name or slug")
    parser.add_argument("--clip", "-c", required=True, help="Clip ID to evaluate")
    parser.add_argument("--scores", "-s", type=str, help="JSON dict of NSFW chain QA scores")
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

    scores = json.loads(args.scores) if args.scores else None
    if scores:
        qa = evaluate_nsfw_chain_qa(clip, scores)
        clip["nsfw_chain_qa"] = qa
        if qa["decision"] == "go":
            clip["status"] = "approved"
        elif qa["decision"] == "no_go":
            clip["status"] = "qa_hold"
        save_nsfw_sequence(seq)
    else:
        qa = run_nsfw_chain_qa_scaffold(clip)

    print(json.dumps(qa, indent=2))
    if qa.get("decision") != "awaiting_scores":
        print(f"\nDecision: {qa['decision']}")


if __name__ == "__main__":
    main()