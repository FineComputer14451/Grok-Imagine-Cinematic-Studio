#!/usr/bin/env python3
"""Async batch video upscaler — processes multiple clips in parallel."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def _load_upscaler():
    spec = importlib.util.spec_from_file_location(
        "ai_video_upscale", SCRIPT_DIR / "ai_video_upscale.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _process_clip(args_tuple: tuple) -> dict:
    input_path, output_path, scale, model, face_restore, crf, force_pure = args_tuple
    mod = _load_upscaler()
    return mod.upscale_video(
        Path(input_path),
        Path(output_path),
        scale=scale,
        model_name=model,
        face_restore=face_restore,
        crf=crf,
        force_pure=force_pure,
    )


def collect_inputs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    extensions = {".mp4", ".mov", ".mkv", ".webm", ".avi"}
    return sorted(p for p in input_path.iterdir() if p.suffix.lower() in extensions)


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch async video upscaler")
    parser.add_argument("--input", "-i", required=True, type=Path, help="Video file or directory")
    parser.add_argument("--output", "-o", required=True, type=Path, help="Output file or directory")
    parser.add_argument("--scale", "-s", type=int, default=2, choices=[2, 3, 4])
    parser.add_argument("--model", "-m", default="realesrgan-x4plus")
    parser.add_argument("--face-restore", action="store_true")
    parser.add_argument("--crf", type=int, default=18)
    parser.add_argument("--workers", "-w", type=int, default=4)
    parser.add_argument("--force-pure", action="store_true")
    args = parser.parse_args()

    inputs = collect_inputs(args.input)
    if not inputs:
        print(f"ERROR: no video files found in {args.input}", file=sys.stderr)
        sys.exit(1)

    args.output.mkdir(parents=True, exist_ok=True) if len(inputs) > 1 or args.input.is_dir() else args.output.parent.mkdir(parents=True, exist_ok=True)

    tasks = []
    for clip in inputs:
        if len(inputs) == 1 and not args.input.is_dir():
            out = args.output
        else:
            out = args.output / f"{clip.stem}_upscaled{clip.suffix}"
        tasks.append((str(clip), str(out), args.scale, args.model, args.face_restore, args.crf, args.force_pure))

    print(f"Processing {len(tasks)} clip(s) with {args.workers} worker(s)")
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_process_clip, t): t[0] for t in tasks}
        for future in as_completed(futures):
            src = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"  ✓ {src} → {result['output']} ({result['method']}, {result['elapsed_seconds']}s)")
            except Exception as exc:
                print(f"  ✗ {src}: {exc}", file=sys.stderr)

    print(f"\nCompleted {len(results)}/{len(tasks)} clips")
    if len(results) < len(tasks):
        sys.exit(1)


if __name__ == "__main__":
    main()