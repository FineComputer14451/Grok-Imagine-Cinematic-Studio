#!/usr/bin/env bash
#
# Grok Doctor — health check for Grok Build + Grok Imagine Cinematic Studio
#
# Usage:
#   bash scripts/grok_doctor.sh
#   bash scripts/grok_doctor.sh --quick
#   bash scripts/grok_doctor.sh --json
#   cinematic-studio doctor
#   grok-doctor
#
# Env:
#   CINEMATIC_REPO_ROOT   Override git checkout path
#   CINEMATIC_PROJECT_DIR Override Method A project dir (default ~/Grok-Cinematic-Projects)
#

set -euo pipefail

QUICK=0
JSON=0
STRICT=0

for arg in "$@"; do
  case "$arg" in
    --quick|-q) QUICK=1 ;;
    --json) JSON=1 ;;
    --strict) STRICT=1 ;;
    -h|--help|help)
      cat <<'EOF'
Grok Doctor — Grok Build + Cinematic Studio health check

Usage:
  grok_doctor.sh [--quick] [--json] [--strict]

  --quick   Skip pytest and full plugin verify
  --json    Emit machine-readable summary (exit code still reflects health)
  --strict  Exit 1 if any warning (not only failures)
EOF
      exit 0
      ;;
  esac
done

# Resolve repo root (prefer this script's parent, then env, then common paths)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${CINEMATIC_REPO_ROOT:-}"
if [[ -z "$REPO_ROOT" && -f "$SCRIPT_DIR/../VERSION" ]]; then
  REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
elif [[ -z "$REPO_ROOT" && -f "$SCRIPT_DIR/VERSION" ]]; then
  REPO_ROOT="$SCRIPT_DIR"
elif [[ -z "$REPO_ROOT" && -f "${HOME}/Grok-Imagine-Cinematic-Studio/VERSION" ]]; then
  REPO_ROOT="${HOME}/Grok-Imagine-Cinematic-Studio"
fi
PROJECT_DIR="${CINEMATIC_PROJECT_DIR:-$HOME/Grok-Cinematic-Projects}"

PASS=0
FAIL=0
WARN=0
declare -a REPORT_LINES=()

_ok()   { PASS=$((PASS + 1)); REPORT_LINES+=("PASS|$1|$2"); [[ "$JSON" -eq 1 ]] || printf '  ✅ %s — %s\n' "$1" "$2"; }
_fail() { FAIL=$((FAIL + 1)); REPORT_LINES+=("FAIL|$1|$2"); [[ "$JSON" -eq 1 ]] || printf '  ❌ %s — %s\n' "$1" "$2"; }
_warn() { WARN=$((WARN + 1)); REPORT_LINES+=("WARN|$1|$2"); [[ "$JSON" -eq 1 ]] || printf '  ⚠️  %s — %s\n' "$1" "$2"; }
_sec()  { [[ "$JSON" -eq 1 ]] || printf '\n── %s ──\n' "$1"; }

[[ "$JSON" -eq 1 ]] || {
  echo "════════════════════════════════════════"
  echo " GROK DOCTOR · $(date -Iseconds)"
  echo " Studio doctor for Grok Build + Cinematic Studio"
  echo "════════════════════════════════════════"
}

# 1. Grok Build CLI
_sec "1. Grok Build CLI"
if command -v grok >/dev/null 2>&1; then
  GROK_VER="$(grok --version 2>/dev/null | head -1 || true)"
  _ok "grok binary" "${GROK_VER:-found} ($(command -v grok))"
  # parse version if possible
  if [[ "$GROK_VER" =~ ([0-9]+\.[0-9]+\.[0-9]+) ]]; then
    ver="${BASH_REMATCH[1]}"
    # crude semver compare for min 0.2.93
    IFS=. read -r a b c <<<"$ver"
    if (( a > 0 || (a == 0 && b > 2) || (a == 0 && b == 2 && c >= 93) )); then
      _ok "grok CLI min version" "$ver ≥ 0.2.93"
    else
      _fail "grok CLI min version" "$ver < 0.2.93 (upgrade Grok Build)"
    fi
  fi
else
  _fail "grok binary" "not on PATH"
fi

if command -v cinematic-studio >/dev/null 2>&1; then
  CS_VER="$(cinematic-studio version 2>/dev/null | head -1 || true)"
  _ok "cinematic-studio" "${CS_VER:-found}"
else
  _warn "cinematic-studio" "not on PATH (run install or add ~/.grok/bin)"
fi

# 2. Auth / config
_sec "2. Auth & config"
if [[ -f "$HOME/.grok/auth.json" ]]; then
  _ok "auth.json" "present"
else
  _fail "auth.json" "missing — run grok login / authenticate"
fi
if [[ -f "$HOME/.grok/config.toml" ]]; then
  _ok "config.toml" "present"
  if grep -q 'default\s*=\s*"grok-4.5"' "$HOME/.grok/config.toml" 2>/dev/null; then
    _ok "models.default" "grok-4.5"
  else
    _warn "models.default" "not set to grok-4.5 (check ~/.grok/config.toml)"
  fi
  if grep -q 'fork_secondary_model\s*=\s*"grok-build"' "$HOME/.grok/config.toml" 2>/dev/null; then
    _ok "fork_secondary_model" "grok-build"
  else
    _warn "fork_secondary_model" "expected grok-build"
  fi
else
  _warn "config.toml" "missing — optional; copy config/grok-build.example.toml"
fi

# 3. Versions
_sec "3. Studio VERSION"
REPO_V="?"
PROJ_V="?"
[[ -n "$REPO_ROOT" && -f "$REPO_ROOT/VERSION" ]] && REPO_V="$(tr -d '[:space:]' < "$REPO_ROOT/VERSION")"
[[ -f "$PROJECT_DIR/VERSION" ]] && PROJ_V="$(tr -d '[:space:]' < "$PROJECT_DIR/VERSION")"
if [[ "$REPO_V" != "?" ]]; then
  _ok "repo VERSION" "$REPO_V ($REPO_ROOT)"
else
  _warn "repo VERSION" "checkout not found (set CINEMATIC_REPO_ROOT)"
fi
if [[ "$PROJ_V" != "?" ]]; then
  _ok "PROJECT_DIR VERSION" "$PROJ_V ($PROJECT_DIR)"
  if [[ "$REPO_V" != "?" && "$REPO_V" != "$PROJ_V" ]]; then
    _warn "VERSION drift" "repo=$REPO_V project=$PROJ_V — run cinematic-studio update"
  fi
else
  _warn "PROJECT_DIR VERSION" "Method A project missing — optional if plugin-only"
fi

# 4. Models
_sec "4. Model stack"
MODELS_OK=0
if [[ -n "$REPO_ROOT" && -f "$REPO_ROOT/tools/cinematic_studio_cli.py" ]]; then
  if (cd "$REPO_ROOT" && python3 tools/cinematic_studio_cli.py models verify >/tmp/grok-doctor-models.txt 2>&1); then
    if grep -q 'Model compatibility verified' /tmp/grok-doctor-models.txt 2>/dev/null; then
      _ok "models verify" "compatible (studio target in report)"
      MODELS_OK=1
    else
      _warn "models verify" "ran but no verified banner — see /tmp/grok-doctor-models.txt"
    fi
  else
    _fail "models verify" "failed — see /tmp/grok-doctor-models.txt"
  fi
elif command -v cinematic-studio >/dev/null 2>&1; then
  if cinematic-studio models verify >/tmp/grok-doctor-models.txt 2>&1; then
    _ok "models verify" "compatible"
    MODELS_OK=1
  else
    _fail "models verify" "failed"
  fi
else
  _warn "models verify" "no CLI available"
fi
[[ "$MODELS_OK" -eq 1 && "$JSON" -eq 0 ]] && grep -E 'Studio target|Installed CLI|xAI Chat|Imagine' /tmp/grok-doctor-models.txt 2>/dev/null | sed 's/^/     /' | head -8

# 5. Plugin
_sec "5. Cinematic plugin"
if command -v grok >/dev/null 2>&1; then
  if grok plugin list 2>/dev/null | grep -qi 'grok-imagine-cinematic-studio'; then
    _ok "plugin installed" "grok-imagine-cinematic-studio listed"
    DETAIL="$(grok plugin details grok-imagine-cinematic-studio 2>/dev/null || true)"
    if echo "$DETAIL" | grep -q 'skill dir'; then
      SKILLS_N="$(echo "$DETAIL" | grep -oE '[0-9]+ skill dir' | head -1 || true)"
      _ok "plugin components" "${SKILLS_N:-present}"
    fi
    if echo "$DETAIL" | grep -qE 'v3\.8\.[0-9]+'; then
      PV="$(echo "$DETAIL" | grep -oE 'v3\.8\.[0-9]+' | head -1)"
      _ok "plugin version stamp" "$PV"
    fi
  else
    _fail "plugin installed" "not found — grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust"
  fi
else
  _warn "plugin" "skipped (no grok)"
fi

# 6. Catalog pin (repo only)
_sec "6. Plugin catalog pin"
if [[ -n "$REPO_ROOT" && -f "$REPO_ROOT/tools/cinematic_studio_cli.py" ]]; then
  if (cd "$REPO_ROOT" && python3 tools/cinematic_studio_cli.py plugin catalog check --release >/tmp/grok-doctor-catalog.txt 2>&1); then
    _ok "catalog pin" "release check green"
  else
    _warn "catalog pin" "check failed or not a full checkout — see /tmp/grok-doctor-catalog.txt"
  fi
else
  _warn "catalog pin" "skipped (no repo tools)"
fi

# 7. Skills layout
_sec "7. Skills layout"
if [[ -n "$REPO_ROOT" && -d "$REPO_ROOT/.grok/skills" ]]; then
  DISK_N="$(find "$REPO_ROOT/.grok/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
  _ok "repo skill dirs" "$DISK_N"
  MISS=0
  for d in "$REPO_ROOT"/.grok/skills/*/SKILL.md; do
    [[ -f "$d" ]] || continue
    grep -q model_compatibility "$d" || MISS=$((MISS + 1))
  done
  if [[ "$MISS" -eq 0 ]]; then
    _ok "model_compatibility" "all SKILL.md present"
  else
    _warn "model_compatibility" "$MISS skill(s) missing YAML block"
  fi
fi
USER_N="$(find "$HOME/.grok/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
_ok "user ~/.grok/skills" "${USER_N:-0} dirs (studio skills should live in plugin after declutter)"

# 8. Plugin verify
if [[ "$QUICK" -eq 0 ]]; then
  _sec "8. verify --plugin"
  if [[ -n "$REPO_ROOT" && -f "$REPO_ROOT/scripts/cinematic_studio.sh" ]]; then
    if bash "$REPO_ROOT/scripts/cinematic_studio.sh" verify --plugin >/tmp/grok-doctor-verify.txt 2>&1; then
      _ok "verify --plugin" "passed"
    else
      _fail "verify --plugin" "failed — see /tmp/grok-doctor-verify.txt"
    fi
  else
    _warn "verify --plugin" "skipped (no scripts)"
  fi
fi

# 9. Git
_sec "9. Git"
if [[ -n "$REPO_ROOT" && -d "$REPO_ROOT/.git" ]]; then
  BRANCH="$(git -C "$REPO_ROOT" status -sb 2>/dev/null | head -1)"
  TAG="$(git -C "$REPO_ROOT" describe --tags --always 2>/dev/null || true)"
  _ok "git" "${BRANCH:-?} · ${TAG:-?}"
  if git -C "$REPO_ROOT" status --porcelain 2>/dev/null | grep -q .; then
    _warn "working tree" "dirty (local changes present)"
  else
    _ok "working tree" "clean"
  fi
else
  _warn "git" "not a git checkout"
fi

# 10. Secrets / API (presence only)
_sec "10. API keys (presence only)"
if [[ -n "${XAI_API_KEY:-}" ]]; then
  _ok "XAI_API_KEY" "set in environment"
else
  _warn "XAI_API_KEY" "unset (API Imagine CLI spend may fail; Build may use auth.json)"
fi
if [[ -f "$HOME/.grok/secrets.env" ]]; then
  _ok "secrets.env" "present"
else
  _warn "secrets.env" "absent (optional)"
fi

# 11. GitHub CLI
_sec "11. GitHub CLI"
if command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then
    WHO="$(gh api user --jq .login 2>/dev/null || echo authenticated)"
    _ok "gh auth" "$WHO"
  else
    _warn "gh auth" "not logged in"
  fi
else
  _warn "gh" "not installed"
fi

# 12. Tests
if [[ "$QUICK" -eq 0 && -n "$REPO_ROOT" && -d "$REPO_ROOT/tests" ]]; then
  _sec "12. Quick tests"
  if (cd "$REPO_ROOT" && python3 -m pytest tests/test_plugin_packs.py tests/test_agents_registry.py -q --tb=no >/tmp/grok-doctor-pytest.txt 2>&1); then
    TAIL="$(tail -1 /tmp/grok-doctor-pytest.txt 2>/dev/null || true)"
    _ok "pytest packs/agents" "${TAIL:-passed}"
  else
    _fail "pytest packs/agents" "failed — see /tmp/grok-doctor-pytest.txt"
  fi
fi

# Summary
if [[ "$JSON" -eq 1 ]]; then
  REPORT_FILE="$(mktemp)"
  printf '%s\n' "${REPORT_LINES[@]}" >"$REPORT_FILE"
  python3 - "$PASS" "$FAIL" "$WARN" "$REPO_V" "$PROJ_V" "$REPO_ROOT" "$PROJECT_DIR" "$REPORT_FILE" <<'PYJSON'
import json, sys
pass_n, fail_n, warn_n, repo_v, proj_v, repo_root, project_dir, report_file = sys.argv[1:9]
checks = []
with open(report_file, encoding="utf-8") as fh:
    for line in fh:
        line = line.rstrip("\n")
        if not line:
            continue
        parts = line.split("|", 2)
        if len(parts) == 3:
            checks.append({"status": parts[0], "name": parts[1], "detail": parts[2]})
payload = {
    "pass": int(pass_n),
    "fail": int(fail_n),
    "warn": int(warn_n),
    "repo_version": repo_v,
    "project_version": proj_v,
    "repo_root": repo_root,
    "project_dir": project_dir,
    "checks": checks,
    "healthy": int(fail_n) == 0,
}
print(json.dumps(payload, indent=2))
PYJSON
  rm -f "$REPORT_FILE"
else
  echo ""
  echo "════════════════════════════════════════"
  echo " SUMMARY"
  echo "════════════════════════════════════════"
  printf '  ✅ pass: %s   ❌ fail: %s   ⚠️  warn: %s\n' "$PASS" "$FAIL" "$WARN"
  if [[ "$FAIL" -eq 0 ]]; then
    echo "  Verdict: HEALTHY"
    echo "  Activate: Activate Grok Imagine Cinematic Studio v${REPO_V}"
  else
    echo "  Verdict: NEEDS ATTENTION"
  fi
  echo "════════════════════════════════════════"
fi

if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
if [[ "$STRICT" -eq 1 && "$WARN" -gt 0 ]]; then
  exit 1
fi
exit 0
