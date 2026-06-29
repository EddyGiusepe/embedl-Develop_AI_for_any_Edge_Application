#!/usr/bin/env bash
# Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
# Shortcut to start the backend in development mode:

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "Starting backend_embedl at http://$HOST:$PORT"
echo "Documentation: http://$HOST:$PORT/docs"
echo ""

uv run uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
