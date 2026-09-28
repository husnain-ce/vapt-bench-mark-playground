#!/usr/bin/env bash
# Create the shared external docker bridge every compose file attaches to.
# Idempotent — safe to re-run. Must run BEFORE any compose up.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

if docker network inspect "$RANGE_NET" >/dev/null 2>&1; then
  ok "network '$RANGE_NET' already exists"
else
  log "creating docker network '$RANGE_NET' ($RANGE_SUBNET)"
  docker network create \
    --driver bridge \
    --subnet "$RANGE_SUBNET" \
    --gateway "$RANGE_GATEWAY" \
    "$RANGE_NET" >/dev/null
  ok "network '$RANGE_NET' created"
fi
