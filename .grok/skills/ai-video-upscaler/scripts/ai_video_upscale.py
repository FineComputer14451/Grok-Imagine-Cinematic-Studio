#!/usr/bin/env python3
"""AI video upscaler with Real-ESRGAN GPU path and pure-Python fallback."""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MODELS_DIR = SCRIPT_DIR.parent / "models"


def gpu_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def realesrgan_available() -> bool:
    return importlib.util.find_spec("realesrgan") is not None


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


def assemble_video(frames_dir: Path, output: Path, fps: float, crf: int, audio_src: Path) -> None:
    pattern = str(frames_dir / "frame_%06d.png")
    cmd = [
        "ffmpeg", "-y", "-framerate", str(fps), "-i", pattern,
        "-i", str(audio_src),
        "-c:v", "libx264", "-crf", str(crf), "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def restore_faces(frames_dir: Path, model_path: Path) -> None:
    try:
        from gfpgan import GFPGANer
        import cv2
    except ImportError:
        print("WARNING: gfpgan not installed, skipping face restoration", file=sys.stderr)
        return

    if not model_path.exists():
        print(f"WARNING: GFPGAN model not found at {model_path}, skipping face restoration", file=sys.stderr)
        return

    restorer = GFPGANer(
        model_path=str(model_path),
        upscale=1,
        arch="clean",
        channel_multiplier=2,
        bg_upsampler=None,
    )

    frames = sorted(frames_dir.glob("frame_*.png"))
    for i, frame_path in enumerate(frames, 1):
        img = cv2.imread(str(frame_path), cv2.IMREAD_COLOR)
        _, _, restored = restorer.enhance(img, has_aligned=False, only_center_face=False, paste_back=True)
        cv2.imwrite(str(frame_path), restored)
        if i % 30 == 0 or i == len(frames):
            print(f"  [{i}/{len(frames)}] frames face-restored")


def upscale_frames_gpu(frames_in: Path, frames_out: Path, model_name: str, scale: int) -> None:
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer
    import cv2

    model_file = MODELS_DIR / f"{model_name}.pth"
    if not model_file.exists():
        raise FileNotFoundError(
            f"Model not found: {model_file}. Run: bash scripts/install_models.sh"
        )

    if model_name == "realesrgan-x4plus":
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        netscale = 4
    elif model_name == "realesrgan-x4plus-anime":
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
        netscale = 4
    else:
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
        netscale = 2

    upsampler = RealESRGANer(
        scale=netscale,
        model_path=str(model_file),
        model=model,
        tile=400,
        tile_pad=10,
        pre_pad=0,
        half=gpu_available(),
    )

    frames = sorted(frames_in.glob("frame_*.png"))
    for i, frame_path in enumerate(frames, 1):
        img = cv2.imread(str(frame_path), cv2.IMREAD_COLOR)
        output, _ = upsampler.enhance(img, outscale=scale)
        cv2.imwrite(str(frames_out / frame_path.name), output)
        if i % 10 == 0 or i == len(frames):
            print(f"  [{i}/{len(frames)}] frames upscaled (Real-ESRGAN)")


def upscale_video(
    input_path: Path,
    output_path: Path,
    scale: int = 2,
    model_name: str = "realesrgan-x4plus",
    face_restore: bool = False,
    crf: int = 18,
    force_pure: bool = False,
) -> dict:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required but not found in PATH")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    use_gpu = not force_pure and gpu_available() and realesrgan_available()
    method = "realesrgan-gpu" if use_gpu else "pure-python-fallback"

    start = time.time()

    with tempfile.TemporaryDirectory(prefix="upscale_") as tmp:
        tmp_path = Path(tmp)
        frames_in = tmp_path / "in"
        frames_out = tmp_path / "out"
        frames_in.mkdir()
        frames_out.mkdir()

        fps = extract_frames(input_path, frames_in)
        frames = sorted(frames_in.glob("frame_*.png"))
        if not frames:
            raise RuntimeError(f"No frames extracted from {input_path}")

        if use_gpu:
            try:
                upscale_frames_gpu(frames_in, frames_out, model_name, scale)
            except Exception as exc:
                print(f"GPU upscale failed ({exc}), falling back to pure Python", file=sys.stderr)
                method = "pure-python-fallback"
                use_gpu = False

        if not use_gpu:
            pure_script = SCRIPT_DIR / "ai_video_upscale_pure.py"
            spec = importlib.util.spec_from_file_location("pure_upscale", pure_script)
            pure_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pure_mod)
            for i, frame in enumerate(frames, 1):
                pure_mod.upscale_frame(frame, frames_out / frame.name, scale)
                if i % 30 == 0 or i == len(frames):
                    print(f"  [{i}/{len(frames)}] frames upscaled (fallback)")

        if face_restore:
            gfpgan_model = MODELS_DIR / "GFPGANv1.4.pth"
            restore_faces(frames_out, gfpgan_model)

        assemble_video(frames_out, output_path, fps, crf, input_path)

    elapsed = time.time() - start
    return {
        "method": method,
        "input": str(input_path),
        "output": str(output_path),
        "scale": scale,
        "frames": len(frames),
        "fps": fps,
        "face_restore": face_restore,
        "elapsed_seconds": round(elapsed, 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="AI video upscaler (GPU + fallback)")
    parser.add_argument("--input", "-i", required=True, type=Path)
    parser.add_argument("--output", "-o", required=True, type=Path)
    parser.add_argument("--scale", "-s", type=int, default=2, choices=[2, 3, 4])
    parser.add_argument("--model", "-m", default="realesrgan-x4plus")
    parser.add_argument("--face-restore", action="store_true")
    parser.add_argument("--crf", type=int, default=18)
    parser.add_argument("--force-pure", action="store_true", help="Force pure-Python fallback")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Upscaling {args.input} → {args.output} (scale={args.scale}x)")
    result = upscale_video(
        args.input, args.output,
        scale=args.scale,
        model_name=args.model,
        face_restore=args.face_restore,
        crf=args.crf,
        force_pure=args.force_pure,
    )
    print(
        f"Done: {result['frames']} frames, method={result['method']}, "
        f"elapsed={result['elapsed_seconds']}s → {result['output']}"
    )


if __name__ == "__main__":
    main()