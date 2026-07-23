#!/usr/bin/env bash
#
# Grok Doctor — thin launcher for the Python health-check registry.
#
# Prefer: cinematic-studio doctor | python tools/cinematic_studio_cli.py doctor
#
# Usage:
#   grok-doctor
#   bash scripts/grok_doctor.sh [--quick] [--json] [--strict]
#
# Resolution order (no hard-coded product clone paths):
#   1. CINEMATIC_CLI_PY
#   2. scripts/../tools (dev checkout / Method A scripts tree)
#   3. CINEMATIC_REPO_ROOT/tools
#   4. CINEMATIC_PROJECT_DIR or ~/Grok-Cinematic-Projects/tools
#   5. cinematic-studio doctor (installed wrapper)
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

_resolve_cli() {
  local candidate=""
  if [[ -n "${CINEMATIC_CLI_PY:-}" && -f "${CINEMATIC_CLI_PY}" ]]; then
    printf '%s\n' "${CINEMATIC_CLI_PY}"
    return 0
  fi
  if [[ -f "${SCRIPT_DIR}/../tools/cinematic_studio_cli.py" ]]; then
    printf '%s\n' "${SCRIPT_DIR}/../tools/cinematic_studio_cli.py"
    return 0
  fi
  if [[ -n "${CINEMATIC_REPO_ROOT:-}" && -f "${CINEMATIC_REPO_ROOT}/tools/cinematic_studio_cli.py" ]]; then
    printf '%s\n' "${CINEMATIC_REPO_ROOT}/tools/cinematic_studio_cli.py"
    return 0
  fi
  local project="${CINEMATIC_PROJECT_DIR:-$HOME/Grok-Cinematic-Projects}"
  if [[ -f "${project}/tools/cinematic_studio_cli.py" ]]; then
    printf '%s\n' "${project}/tools/cinematic_studio_cli.py"
    return 0
  fi
  return 1
}

_python_for_cli() {
  local cli="$1"
  local root
  root="$(cd "$(dirname "$cli")/.." && pwd)"
  if [[ -x "${root}/.venv/bin/python" ]]; then
    printf '%s\n' "${root}/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    printf '%s\n' "python3"
  else
    printf '%s\n' "python"
  fi
}

if cli_py="$(_resolve_cli)"; then
  cli_py="$(cd "$(dirname "$cli_py")" && pwd)/$(basename "$cli_py")"
  root="$(cd "$(dirname "$cli_py")/.." && pwd)"
  export CINEMATIC_REPO_ROOT="${CINEMATIC_REPO_ROOT:-$root}"
  exec "$(_python_for_cli "$cli_py")" "$cli_py" doctor "$@"
fi

if [[ "${GROK_DOCTOR_REENTRY:-}" != "1" ]] && command -v cinematic-studio >/dev/null 2>&1; then
  export GROK_DOCTOR_REENTRY=1
  exec cinematic-studio doctor "$@"
fi

cat >&2 <<'EOF'
❌ Grok Doctor: cinematic_studio_cli.py not found

  Set CINEMATIC_REPO_ROOT, CINEMATIC_CLI_PY, or CINEMATIC_PROJECT_DIR, or install:
    bash scripts/cinematic_studio.sh install
EOF
exit 1
