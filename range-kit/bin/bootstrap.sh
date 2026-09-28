#!/usr/bin/env bash
# One-shot bring-up on a fresh VM. Run as ROOT (edits /etc/hosts + nginx + k3s).
#
#   sudo ./bin/bootstrap.sh              # full range (RAM permitting)
#   sudo ./bin/bootstrap.sh --web-only   # just the loopback web/API labs
#   sudo NO_NGINX=1 ./bin/bootstrap.sh   # skip nginx (reach labs by 127.0.0.1:<port>)
#
# Order: preflight -> network -> /etc/hosts -> nginx -> deploy-all (phased).
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

[ "$(id -u)" -eq 0 ] || die "run as root: sudo $0 $*"

log "### Aqira Benchmark bootstrap ###"
"$BENCH_ROOT/bin/preflight.sh" || die "preflight failed — resolve the issues above and re-run"

"$BENCH_ROOT/bin/create-network.sh"
"$BENCH_ROOT/bin/install-hosts.sh"

if [ "${NO_NGINX:-0}" = 1 ]; then
  warn "NO_NGINX=1 — skipping nginx; labs reachable only by 127.0.0.1:<port>"
else
  "$BENCH_ROOT/bin/install-nginx.sh" || warn "nginx install failed; labs still reachable by 127.0.0.1:<port>"
fi

"$BENCH_ROOT/bin/deploy-all.sh" "$@"

echo
ok "bootstrap finished. Re-run bin/verify.sh anytime; tear down with bin/teardown.sh."
