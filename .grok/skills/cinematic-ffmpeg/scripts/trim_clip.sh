#!/usr/bin/env bash
# Trim a clip by start/duration (seconds).
set -euo pipefail

if [[ $# -lt 4 ]]; then
  echo "Usage: trim_clip.sh <input.mp4> <output.mp4> <start_sec> <duration_sec>" >&2
  exit 2
fi

INPUT="$1"
OUTPUT="$2"
START="$3"
DURATION="$4"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg not found" >&2
  exit 2
fi

mkdir -p "$(dirname "$OUTPUT")"
ffmpeg -y -ss "$START" -i "$INPUT" -t "$DURATION" -c copy "$OUTPUT" 2>/dev/null || \
  ffmpeg -y -ss "$START" -i "$INPUT" -t "$DURATION" -c:v libx264 -c:a aac "$OUTPUT"
echo "✅ Trimmed $INPUT → $OUTPUT (${START}s + ${DURATION}s)"