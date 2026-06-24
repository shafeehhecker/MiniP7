#!/usr/bin/env bash
# Launches the full Mini-P7 stack (API + browser UI) with one command.
# Usage: ./run.sh   then open http://127.0.0.1:8000
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT/packages/schema/src:$ROOT/packages/engine/src:$ROOT/packages/persistence/src:$ROOT/packages/services/src:$ROOT/apps/api/src"
export MINIP7_DB="${MINIP7_DB:-$ROOT/minip7.db}"
echo "Mini-P7 running at http://127.0.0.1:8000   (API docs at /docs)"
exec python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 "$@"
