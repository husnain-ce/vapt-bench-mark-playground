#!/usr/bin/env bash
# vulnerable-api native launcher (the published Docker image uses a REMOVED manifest schema).
set -e
cd "$(dirname "$0")/ansible/roles/api/files"
python3 -m venv venv 2>/dev/null || true
./venv/bin/pip install --disable-pip-version-check bottle lxml
echo "Starting vulnerable-api on http://localhost:8081  (Ctrl-C to stop)"
exec ./venv/bin/python vAPI.py
