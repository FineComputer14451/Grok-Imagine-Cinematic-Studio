#!/usr/bin/env python3
"""Pure-Python video upscale fallback (Lanczos + unsharp mask). No GPU models required."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageFilter
except ImportError:
    print("ERROR: pillow is required. Run: pip install pillow", file=sys.stderr)
    sys.exit(1)


def upscale_frame(src: Path, dst: Path, scale: int) -> None:
    with Image.open(src) as img:
        w, h = img.size
        upscaled = img.resize((w * scale, h * scale), Image.Resampling.LANCZOS)
        upscaled = upscaled.filter(ImageFilter.UnsharpMask(radius=1.5, percent=80, threshold=3))
        upscaled.save(dst, quality=95)


def extract_frames(video: Path, frames_dir: Path) -> float:
    pattern = str(frames_dir / "frame_%06d.png")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video), "-qscale:v", "2", pattern],
        check=True,
        capture_output=True,
    )
    probe = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", str(video),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    rate = probe.stdout.strip()
    if "/" in rate:
        num, den = rate.split("/")
        return float(num) / float(den)
    return float(rate) if rate else 24.0


def assemble_video(frames_dir: Path, output: Path, fps: float, crf: int, audio_src: Path | None) -> None:
    pattern = str(frames_dir / "frame_%06d.png")
    cmd = [
        "ffmpeg", "-y", "-framerate", str(fps), "-i", pattern,
        "-c:v", "libx264", "-crf", str(crf), "-pix_fmt", "yuv420p",
    ]
    if audio_src and audio_src.exists():
        cmd += ["-i", str(audio_src), "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd.append(str(output))
    subprocess.run(cmd, check=True, capture_output=True)


def upscale_video(input_path: Path, output_path: Path, scale: int, crf: int) -> dict:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required but not found in PATH")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="upscale_pure_") as tmp:
        tmp_path = Path(tmp)
        frames_in = tmp_path / "in"
        frames_out = tmp_path / "out"
        frames_in.mkdir()
        frames_out.mkdir()

        fps = extract_frames(input_path, frames_in)
        frames = sorted(frames_in.glob("frame_*.png"))
        if not frames:
            raise RuntimeError(f"No frames extracted from {input_path}")

        for i, frame in enumerate(frames, 1):
            upscale_frame(frame, frames_out / frame.name, scale)
            if i % 30 == 0 or i == len(frames):
                print(f"  [{i}/{len(frames)}] frames upscaled (pure Python)")

        assemble_video(frames_out, output_path, fps, crf, input_path)

    return {
        "method": "pure-python",
        "input": str(input_path),
        "output": str(output_path),
        "scale": scale,
        "frames": len(frames),
        "fps": fps,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Pure-Python video upscale (no GPU)")
    parser.add_argument("--input", "-i", required=True, type=Path)
    parser.add_argument("--output", "-o", required=True, type=Path)
    parser.add_argument("--scale", "-s", type=int, default=2, choices=[2, 3, 4])
    parser.add_argument("--crf", type=int, default=18)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Upscaling {args.input} → {args.output} (scale={args.scale}x, pure Python)")
    result = upscale_video(args.input, args.output, args.scale, args.crf)
    print(f"Done: {result['frames']} frames @ {result['fps']:.2f} fps → {result['output']}")


if __name__ == "__main__":
    main()