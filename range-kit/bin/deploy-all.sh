#!/usr/bin/env bash
# Deploy the whole range in dependency order, with a RAM gate before the heavy
# k3s phase. Each phase is independently re-runnable. Flags let you skip phases.
#
#   --no-net     skip Metasploitable 2/3 (network labs)
#   --no-k8s     skip the k3s / Kubernetes Goat phase (the RAM-hungry one)
#   --no-cloud   skip LocalStack + seed
#   --web-only   only the loopback web/API labs
#
# nginx + /etc/hosts + venv are handled by bootstrap.sh; run that first (as root)
# or run bin/install-hosts.sh and bin/install-nginx.sh yourself.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

DO_NET=1; DO_K8S=1; DO_CLOUD=1
for a in "$@"; do case "$a" in
  --no-net) DO_NET=0 ;;
  --no-k8s) DO_K8S=0 ;;
  --no-cloud) DO_CLOUD=0 ;;
  --web-only) DO_NET=0; DO_K8S=0; DO_CLOUD=0 ;;
  *) die "unknown flag: $a" ;;
esac; done

"$BENCH_ROOT/bin/create-network.sh"

log "=== Phase 1/4: web + API labs ==="
"$BENCH_ROOT/bin/deploy-web.sh"

if [ "$DO_CLOUD" = 1 ]; then
  log "=== Phase 2/4: cloud lab (LocalStack) + IaC static scan ==="
  "$BENCH_ROOT/bin/deploy-cloud.sh"
  log "running IaC static scan (checkov)"
  "$CLOUD_DIR/venv-setup.sh" >/dev/null 2>&1 || true
  bash "$CLOUD_DIR/iac-scan.sh" | tail -5 || warn "iac-scan reported errors"
else warn "skipping cloud phase (--no-cloud)"; fi

if [ "$DO_NET" = 1 ]; then
  log "=== Phase 3/4: network labs (MS2 + MS3-lite) ==="
  "$BENCH_ROOT/bin/deploy-net.sh"
else warn "skipping network phase (--no-net)"; fi

if [ "$DO_K8S" = 1 ]; then
  avail=$(free_mb)
  if [ "$avail" -lt 2500 ] && [ "${FORCE:-0}" != 1 ]; then
    warn "=== Phase 4/4 SKIPPED: only ${avail}MB free (< 2500MB k3s gate). Re-run k8s/deploy-k8s.sh with FORCE=1 when RAM frees up. ==="
  else
    log "=== Phase 4/4: k3s + Kubernetes Goat ==="
    "$K8S_DIR/deploy-k8s.sh"
  fi
else warn "skipping k3s phase (--no-k8s)"; fi

echo
log "deploy complete — verifying..."
"$BENCH_ROOT/bin/verify.sh" || true
