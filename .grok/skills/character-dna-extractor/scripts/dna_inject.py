#!/usr/bin/env python3
"""Output CHARACTER_DNA prompt injection block for Imagine Prompt Master."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

from character_dna import PROMPT_MODES, build_prompt_blocks, find_character_dna, inject_into_prompt, load_character_dna  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CHARACTER_DNA prompt injection")
    parser.add_argument("--name", "-n", required=True, help="Character name or slug")
    parser.add_argument("--mode", "-m", default="cinematic", choices=PROMPT_MODES)
    parser.add_argument("--base-prompt", "-b", default="", help="Optional base prompt to prepend injection onto")
    parser.add_argument("--file", "-f", type=Path, help="Path to dna.json (overrides --name lookup)")
    args = parser.parse_args()

    if args.file:
        dna = load_character_dna(args.file)
        blocks = build_prompt_blocks(dna)
        output = blocks[args.mode]
        if args.base_prompt.strip():
            output = f"{output}\n\n---\n\n{args.base_prompt.strip()}"
    else:
        try:
            output = inject_into_prompt(args.base_prompt, args.name, args.mode)
        except FileNotFoundError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)

    print(output)


if __name__ == "__main__":
    main()