#!/usr/bin/env bash
# Deploy the network labs on static bridge IPs: Metasploitable 2 + MS3-lite.
# ms3 is BUILT from vm/ms3-lite (first run compiles proftpd 1.3.5 from source —
# expect a few minutes and outbound network for apt + the proftpd tarball).
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

"$BENCH_ROOT/bin/create-network.sh"

log "up: metasploitable2 (172.30.0.11)"
dc -f "$COMPOSE_DIR/netlab-ms2.yml" up -d

log "build+up: ms3-lite (172.30.0.12) — first build compiles proftpd 1.3.5, be patient"
dc -f "$COMPOSE_DIR/netlab-ms3.yml" up -d --build

ok "network labs deployed (ms2=172.30.0.11, ms3=172.30.0.12; no host ports)"
warn "KVM Metasploitable 3 is a separate, best-effort path — see docs/KVM-MS3.md"
