#!/usr/bin/env bash
# Install / refresh Grok Build custom NSFW model presets into ~/.grok/config.toml
#
# Usage:
#   bash scripts/install_nsfw_grok_models.sh           # append if missing
#   bash scripts/install_nsfw_grok_models.sh --force    # replace existing NSFW block
#   bash scripts/install_nsfw_grok_models.sh --subagents  # also wire [subagents.models]
#   GROK_CONFIG=/path/to/config.toml bash scripts/install_nsfw_grok_models.sh
#
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/config/grok-build-nsfw-models.example.toml"
CFG="${GROK_CONFIG:-$HOME/.grok/config.toml}"
PERSONAS_SRC="$ROOT/.grok/personas"
PERSONAS_DST="${HOME}/.grok/personas"
MARKER_BEGIN="# --- Grok Imagine Cinematic Studio: custom NSFW models"
FORCE=0
SUBAGENTS=0

for arg in "$@"; do
  case "$arg" in
    --force|-f) FORCE=1 ;;
    --subagents) SUBAGENTS=1 ;;
    --help|-h)
      sed -n '2,12p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 2
      ;;
  esac
done

if [[ ! -f "$SRC" ]]; then
  echo "Missing $SRC" >&2
  exit 1
fi

mkdir -p "$(dirname "$CFG")" "$PERSONAS_DST"
touch "$CFG"

_nsfw_model_blocks() {
  # Emit [model.*] blocks only (skip trailing optional comments)
  sed -n '/^\[model\./,$p' "$SRC" | sed '/^# Optional: default new sessions/,$d'
}

_strip_nsfw_block() {
  # Remove prior install marker + model sections we own
  python3 - "$CFG" <<'PY'
from pathlib import Path
import re
import sys
path = Path(sys.argv[1])
text = path.read_text()
marker = "# --- Grok Imagine Cinematic Studio: custom NSFW models"
idx = text.find(marker)
if idx != -1:
    text = text[:idx].rstrip() + "\n"
# Also strip orphaned [model.nsfw-*] / erosforge-director if marker missing
# but only when they appear as standalone custom blocks we installed.
owned = [
    "erosforge-director",
    "nsfw-prompt-master",
    "nsfw-quota-planner",
    "nsfw-sequence-extend",
    "nsfw-chain-qa",
    "nsfw-identity-lock",
    "nsfw-long-context",
    "nsfw-creative-fast",
]
for name in owned:
    # Match [model.name] ... until next [section] or EOF
    pat = re.compile(
        rf"(?ms)^\[model\.(?:\"{re.escape(name)}\"|{re.escape(name)})\]\n.*?(?=^\[|\Z)"
    )
    text = pat.sub("", text)
path.write_text(text.rstrip() + "\n")
print(f"Stripped existing NSFW model blocks from {path}")
PY
}

if grep -q '\[model\.erosforge-director\]' "$CFG" 2>/dev/null; then
  if [[ "$FORCE" -eq 1 ]]; then
    _strip_nsfw_block
  else
    echo "NSFW models already present in $CFG (use --force to refresh)"
  fi
fi

if ! grep -q '\[model\.erosforge-director\]' "$CFG" 2>/dev/null; then
  {
    echo ""
    echo "${MARKER_BEGIN} (opt-in ErosForge) ---"
    echo "# Session-auth via cli-chat-proxy (SuperGrok). Not paid api.x.ai credits."
    echo "# Registry: tools/models.py → GROK_BUILD_NSFW_MODELS"
    _nsfw_model_blocks
  } >> "$CFG"
  echo "Installed NSFW [model.*] blocks → $CFG"
fi

if [[ "$SUBAGENTS" -eq 1 ]]; then
  if grep -q '\[subagents\.models\]' "$CFG" 2>/dev/null && grep -q 'nsfw-quota-planner\|nsfw-sequence-extend' "$CFG" 2>/dev/null; then
    echo "Subagent NSFW routing already present (skipping)"
  else
    {
      echo ""
      echo "# NSFW opt-in subagent model routing (install_nsfw_grok_models.sh --subagents)"
      echo "[subagents.models]"
      echo 'explore = "nsfw-quota-planner"'
      echo 'plan = "nsfw-sequence-extend"'
    } >> "$CFG"
    echo "Appended [subagents.models] NSFW routing → $CFG"
  fi
fi

if [[ -d "$PERSONAS_SRC" ]]; then
  for f in erosforge.toml nsfw-prompt.toml nsfw-qa.toml; do
    if [[ -f "$PERSONAS_SRC/$f" ]]; then
      cp "$PERSONAS_SRC/$f" "$PERSONAS_DST/$f"
      echo "Installed persona $f → $PERSONAS_DST/"
    fi
  done
fi

echo ""
echo "Verify with:  grok models"
echo "              python tools/cinematic_studio_cli.py models list"
echo "              python tools/cinematic_studio_cli.py models verify"
echo "Switch with:  /model erosforge-director"
echo "Personas:     /personas  (erosforge, nsfw-prompt, nsfw-qa)"
echo "Remember:     ACTIVATE EROSFORGE before intimate production"
echo "Imagine:      stills/video still use grok-imagine-* (not these chat aliases)"
