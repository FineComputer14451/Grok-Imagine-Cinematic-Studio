#!/usr/bin/env bash
# Install / refresh full Grok V9 + Auto specialist picker surface into ~/.grok/config.toml
#
# Usage:
#   bash scripts/install_v9_grok_models.sh           # install / upgrade if incomplete
#   bash scripts/install_v9_grok_models.sh --force    # replace all owned blocks
#   GROK_CONFIG=/path/to/config.toml bash scripts/install_v9_grok_models.sh
#
# Registers every Model Layer alias as a Grok Build [model.*] picker so
#   /model chat-expert · /model multi · /model grok-v9 · /model auto
# never return "unknown model id". All wrap grok-4.5 via cli-chat-proxy.
#
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/config/grok-build-v9-models.example.toml"
CFG="${GROK_CONFIG:-$HOME/.grok/config.toml}"
MARKER_BEGIN="# --- Grok Imagine Cinematic Studio: v9-4p5 specialist models"
FORCE=0

# All [model.*] section names owned by this installer (must match example toml)
OWNED_MODELS=(
  grok-v9-4p5-chat-expert
  grok-v9
  grok-v9-4p5
  v9
  v9-4p5
  chat-expert
  v9-4p5-chat-expert
  4p5-expert
  grok-4.5-expert
  grok-v9-4p5-multi
  multi
  v9-4p5-multi
  4p5-multi
  grok-4.5-multi
  grok-4-auto
  auto
  4-auto
  grok-auto
)

for arg in "$@"; do
  case "$arg" in
    --force|-f) FORCE=1 ;;
    --help|-h)
      sed -n '2,16p' "$0"
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

mkdir -p "$(dirname "$CFG")"
touch "$CFG"

_v9_model_blocks() {
  sed -n '/^\[model\./,$p' "$SRC"
}

_strip_v9_block() {
  python3 - "$CFG" "${OWNED_MODELS[@]}" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
owned = sys.argv[2:]
text = path.read_text()
marker = "# --- Grok Imagine Cinematic Studio: v9-4p5 specialist models"
idx = text.find(marker)
if idx != -1:
    text = text[:idx].rstrip() + "\n"
for name in owned:
    # Match bare or quoted TOML headers (dots require quotes: [model."grok-4.5-expert"])
    pat = re.compile(
        rf"(?ms)^\[model\.(?:\"{re.escape(name)}\"|{re.escape(name)})\]\n.*?(?=^\[|\Z)"
    )
    text = pat.sub("", text)
path.write_text(text.rstrip() + "\n")
print(f"Stripped existing v9 specialist model blocks from {path}")
PY
}

_needs_upgrade() {
  python3 - "$CFG" "${OWNED_MODELS[@]}" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
owned = sys.argv[2:]
text = path.read_text()
for name in owned:
    m = re.search(
        rf"(?ms)^\[model\.(?:\"{re.escape(name)}\"|{re.escape(name)})\]\n(.*?)(?=^\[|\Z)",
        text,
    )
    if not m:
        print("missing")
        raise SystemExit(0)
    body = m.group(1)
    if "temperature" not in body or "not on this team" in body:
        print("stub")
        raise SystemExit(0)
print("ok")
PY
}

status="$(_needs_upgrade)"
if [[ "$status" == "ok" && "$FORCE" -eq 0 ]]; then
  echo "Grok V9 specialist models already complete in $CFG (use --force to refresh)"
else
  # strip if any owned name or marker present
  if grep -q "$MARKER_BEGIN" "$CFG" 2>/dev/null \
    || grep -qE '\[model\.(grok-v9|grok-v9-4p5|chat-expert|grok-v9-4p5-chat-expert|grok-v9-4p5-multi|grok-4-auto)\]' "$CFG" 2>/dev/null; then
    _strip_v9_block
  fi
  {
    echo ""
    echo "${MARKER_BEGIN} (Model Layer v4.5 · full alias surface) ---"
    echo "# Session-auth via cli-chat-proxy (SuperGrok). Base model: grok-4.5."
    echo "# Native API IDs grok-v9-4p5-* / grok-4-auto are not public product slugs."
    echo "# Family shorts + chat-expert / multi / auto aliases all registered as pickers."
    echo "# Registry: tools/models.py → GROK_BUILD_V9_MODELS"
    _v9_model_blocks
  } >> "$CFG"
  echo "Installed full Grok V9 [model.*] picker surface → $CFG"
fi

echo ""
echo "Verify with:  grok models"
echo "              python tools/cinematic_studio_cli.py models list"
echo "              python tools/cinematic_studio_cli.py models verify"
echo "Switch with:  /model grok-v9"
echo "              /model chat-expert"
echo "              /model multi"
echo "              /model auto"
echo "              /model grok-v9-4p5-chat-expert"
echo "Stack default for Bibles/coding remains grok-4.5 (set [models] default separately)."
echo "Imagine:      stills/video still use grok-imagine-* (not these chat aliases)"