#!/usr/bin/env bash
# Center-crop video to target aspect (9:16, 1:1, 16:9).
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: social_crop.sh <input.mp4> <output.mp4> <9:16|1:1|16:9>" >&2
  exit 2
fi

INPUT="$1"
OUTPUT="$2"
ASPECT="$3"

case "$ASPECT" in
  9:16) FILTER="crop=ih*9/16:ih:(iw-ih*9/16)/2:0" ;;
  1:1)  FILTER="crop=ih:ih:(iw-ih)/2:0" ;;
  16:9) FILTER="scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" ;;
  *) echo "Unknown aspect: $ASPECT" >&2; exit 2 ;;
esac

mkdir -p "$(dirname "$OUTPUT")"
ffmpeg -y -i "$INPUT" -vf "$FILTER" -c:a copy "$OUTPUT"
echo "✅ Cropped $INPUT → $OUTPUT ($ASPECT)"