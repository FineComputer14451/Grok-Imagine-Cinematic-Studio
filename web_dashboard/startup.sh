#!/bin/sh
set -eu
cd /workspace

# Snapshot API (FastAPI) — React proxies /api and /health here
if ! curl -sf -o /dev/null --max-time 2 http://127.0.0.1:8787/health; then
  PYTHONPATH=/workspace python -m uvicorn api.app.main:app \
    --host 127.0.0.1 --port 8787 \
    >>/tmp/api-startup.log 2>&1 &
fi

# App preview
if curl -sf -o /dev/null --max-time 2 http://127.0.0.1:8080/; then
  exit 0
fi
npm run dev >>/tmp/app-startup.log 2>&1 &
