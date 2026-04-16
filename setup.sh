#!/usr/bin/env bash
# Local dev setup - no Docker needed.
# Requires: Python 3.12, Node.js 18+
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$ROOT/backend/data"
DB_PATH="$DATA_DIR/invoice_ledger.duckdb"
VENV="$ROOT/.venv"

mkdir -p "$DATA_DIR"

if [ ! -d "$VENV" ]; then
  echo "==> Creating Python venv"
  python3.12 -m venv "$VENV"
fi

PIP="$VENV/bin/pip"

echo "==> Installing dbt-duckdb"
"$PIP" install --quiet dbt-duckdb==1.8.1

echo "==> Running dbt seed + run"
cd "$ROOT/backend/dbt"
DBT_DUCKDB_PATH="$DB_PATH" "$VENV/bin/dbt" seed --profiles-dir .
DBT_DUCKDB_PATH="$DB_PATH" "$VENV/bin/dbt" run  --profiles-dir .
cd "$ROOT"

echo "==> Installing backend dependencies"
"$PIP" install --quiet -r "$ROOT/backend/requirements.txt"

echo "==> Starting FastAPI on http://localhost:8000"
cd "$ROOT/backend"
DUCKDB_PATH="$DB_PATH" "$VENV/bin/uvicorn" main:app --reload --port 8000 &
BACKEND_PID=$!
cd "$ROOT"

echo "==> Installing frontend dependencies"
cd "$ROOT/frontend"
npm install --silent

echo "==> Starting Vite on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!
cd "$ROOT"

echo ""
echo "  Frontend : http://localhost:5173"
echo "  API docs : http://localhost:8000/docs"
echo ""
echo "  Ctrl+C to stop."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" INT TERM
wait
