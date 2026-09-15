#!/usr/bin/env bash
# One-command native start. Uses system python3 if Flask is present,
# otherwise spins a throwaway venv and installs Flask into it.
set -e
cd "$(dirname "$0")"
if python3 -c "import flask" 2>/dev/null; then
  exec python3 app.py
else
  [ -d .venv ] || python3 -m venv .venv
  ./.venv/bin/pip -q install flask
  exec ./.venv/bin/python app.py
fi
