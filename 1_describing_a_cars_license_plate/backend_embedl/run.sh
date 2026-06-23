#!/usr/bin/env bash
# Atalho para iniciar o backend em modo desenvolvimento.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "Iniciando backend_embedl em http://$HOST:$PORT"
echo "Documentacao: http://$HOST:$PORT/docs"
echo ""

uv run uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
