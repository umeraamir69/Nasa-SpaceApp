#!/usr/bin/env bash
# EchoLens one-command demo — starts API + Vite and opens the map.
# Usage (from repo root): ./demo.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-5173}"
HOST="${HOST:-127.0.0.1}"

if [[ ! -x "$ROOT/venv/bin/uvicorn" ]]; then
  echo "Missing venv/bin/uvicorn. From repo root:"
  echo "  python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

if [[ ! -d "$ROOT/web/node_modules" ]]; then
  echo "Missing web/node_modules. From repo root:"
  echo "  cd web && npm install --cache ../.npm-cache"
  exit 1
fi

if [[ ! -f "$ROOT/outputs/snyder/summary.json" ]]; then
  echo "Missing outputs/snyder/summary.json — map has nothing to show."
  exit 1
fi

cleanup() {
  [[ -n "${API_PID:-}" ]] && kill "$API_PID" 2>/dev/null || true
  [[ -n "${WEB_PID:-}" ]] && kill "$WEB_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "API  → http://${HOST}:${API_PORT}"
"$ROOT/venv/bin/uvicorn" app.main:app --host "$HOST" --port "$API_PORT" &
API_PID=$!

echo "Web  → http://${HOST}:${WEB_PORT}"
(
  cd "$ROOT/web"
  npm run dev -- --host "$HOST" --port "$WEB_PORT"
) &
WEB_PID=$!

# Wait until the UI answers, then open it.
for _ in $(seq 1 60); do
  if curl -sf "http://${HOST}:${WEB_PORT}/" >/dev/null 2>&1 \
    && curl -sf "http://${HOST}:${API_PORT}/api/cases" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

URL="http://${HOST}:${WEB_PORT}/"
if command -v open >/dev/null 2>&1; then
  open "$URL"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL"
fi

echo "Ready: $URL  (Ctrl-C stops both servers)"
echo "Pitch click path: notes/docs/Pitch.md"
wait
