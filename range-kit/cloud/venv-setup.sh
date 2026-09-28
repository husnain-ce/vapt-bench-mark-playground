#!/usr/bin/env bash
# Create the Python venv the cloud labs need: awslocal (LocalStack seeding) and
# checkov (IaC static analysis). Idempotent — skips if the tools already exist.
source "$(dirname "${BASH_SOURCE[0]}")/../bin/lib.sh"

have python3 || die "python3 not installed"

if [ -x "$RANGE_VENV/bin/awslocal" ] && [ -x "$RANGE_VENV/bin/checkov" ]; then
  ok "venv already provisioned at $RANGE_VENV"
  exit 0
fi

log "creating venv at $RANGE_VENV"
python3 -m venv "$RANGE_VENV" || die "python3 -m venv failed (apt-get install -y python3-venv)"
"$RANGE_VENV/bin/pip" install --quiet --upgrade pip
log "installing awscli-local + checkov (this can take a minute)"
"$RANGE_VENV/bin/pip" install --quiet awscli awscli-local checkov
ok "venv ready: awslocal + checkov installed"
