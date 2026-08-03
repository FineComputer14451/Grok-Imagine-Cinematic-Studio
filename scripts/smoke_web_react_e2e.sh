#!/usr/bin/env bash
# Smoke for web_react — prefers lightweight HTTP smoke (no Chromium).
# Set WEB_REACT_PLAYWRIGHT=1 to also run Playwright (needs free RAM + browsers).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/web_react"

if [[ ! -d node_modules ]]; then
  npm install
fi

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  echo "Expected $ROOT/.venv/bin/python (studio_api)." >&2
  exit 1
fi

npm run test:unit
npm run test:smoke

if [[ "${WEB_REACT_PLAYWRIGHT:-}" == "1" ]]; then
  npx playwright install chromium
  CI=1 npm run test:e2e
  echo "SMOKE web_react e2e (Playwright) PASSED"
fi

echo "SMOKE web_react PASSED"
