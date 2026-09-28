#!/usr/bin/env bash
# Deploy the loopback web/API labs: juice, dvwa, webgoat, vampi, log4shell.
# These are the light labs — safe to bring up immediately.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

"$BENCH_ROOT/bin/create-network.sh"

WEB=(weblab-juice weblab-dvwa apilab-webgoat apilab-vampi weblab-log4shell)
for f in "${WEB[@]}"; do
  log "up: $f"
  dc -f "$COMPOSE_DIR/$f.yml" up -d
done
ok "web/API labs deployed (8101-8105)"
