#!/usr/bin/env bash
# Start studio_api + Vite preview for Playwright (single webServer process group).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
APP="$(cd "$(dirname "$0")/.." && pwd)"
API_PORT="${E2E_API_PORT:-8090}"
APP_PORT="${E2E_APP_PORT:-4173}"
PY="${ROOT}/.venv/bin/python"

cleanup() {
  [[ -n "${API_PID:-}" ]] && kill "$API_PID" 2>/dev/null || true
  [[ -n "${APP_PID:-}" ]] && kill "$APP_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cd "$ROOT"
"$PY" -m uvicorn studio_api.app:create_app --factory --host 127.0.0.1 --port "$API_PORT" &
API_PID=$!

# Wait for API
for _ in $(seq 1 60); do
  if curl -sf "http://127.0.0.1:${API_PORT}/health" >/dev/null; then
    break
  fi
  sleep 0.5
done
curl -sf "http://127.0.0.1:${API_PORT}/health" >/dev/null

cd "$APP"
if [[ ! -d dist ]]; then
  npm run build
fi
# Proxy must match the API port we just started (not hard-coded 8090).
export VITE_API_PROXY_TARGET="http://127.0.0.1:${API_PORT}"
npx vite preview --host 127.0.0.1 --port "$APP_PORT" &
APP_PID=$!

for _ in $(seq 1 60); do
  if curl -sf "http://127.0.0.1:${APP_PORT}/" >/dev/null; then
    break
  fi
  sleep 0.5
done
curl -sf "http://127.0.0.1:${APP_PORT}/" >/dev/null

# Keep the stack alive (Playwright kills the process group on exit).
wait
