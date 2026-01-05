#!/usr/bin/env bash
# Run dev server using the project's Python 3.11 venv
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PY="$BASE_DIR/.venv3.11/bin/python"
if [ ! -x "$VENV_PY" ]; then
  echo "Interpreter not found at $VENV_PY"
  echo "Ensure you created the venv with: python3.11 -m venv .venv3.11"
  exit 2
fi
export FLASK_ENV=development
export PORT=5001
echo "Starting dev server with $VENV_PY"
"$VENV_PY" "$BASE_DIR/app.py"
