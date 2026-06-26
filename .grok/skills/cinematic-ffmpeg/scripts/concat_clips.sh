#!/usr/bin/env bash
# Concatenate MP4 clips in sorted order for delivery rough cuts.
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: concat_clips.sh <input_dir> <output.mp4>" >&2
  exit 2
fi

INPUT_DIR="$1"
OUTPUT="$2"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg not found. Install: apt-get install ffmpeg" >&2
  exit 2
fi

if [[ ! -d "$INPUT_DIR" ]]; then
  echo "Input directory not found: $INPUT_DIR" >&2
  exit 2
fi

mapfile -t CLIPS < <(find "$INPUT_DIR" -maxdepth 1 -type f \( -name '*.mp4' -o -name '*.mov' \) | sort)
if [[ ${#CLIPS[@]} -eq 0 ]]; then
  echo "No .mp4/.mov files in $INPUT_DIR" >&2
  exit 1
fi

LIST_FILE="$(mktemp)"
trap 'rm -f "$LIST_FILE"' EXIT
for clip in "${CLIPS[@]}"; do
  printf "file '%s'\n" "$clip" >> "$LIST_FILE"
done

mkdir -p "$(dirname "$OUTPUT")"
ffmpeg -y -f concat -safe 0 -i "$LIST_FILE" -c copy "$OUTPUT"
echo "✅ Concatenated ${#CLIPS[@]} clips → $OUTPUT"