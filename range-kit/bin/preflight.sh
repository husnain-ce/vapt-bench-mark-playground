#!/usr/bin/env bash
# Preflight — verify the target VM can host the range before we deploy anything.
# Non-destructive. Exits non-zero if a hard requirement is missing.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

fail=0
softfail=0

log "Aqira Benchmark preflight on $(hostname)"

# --- Hard requirements -------------------------------------------------------
if have docker; then ok "docker: $(docker --version | awk '{print $3}' | tr -d ,)"; else err "docker not found (required)"; fail=1; fi
if docker compose version >/dev/null 2>&1; then ok "docker compose (plugin) present"
elif have docker-compose; then ok "docker-compose (standalone) present"
else err "docker compose / docker-compose not found (required)"; fail=1; fi

if have curl; then ok "curl present"; else err "curl not found (required for verify)"; fail=1; fi
if have git;  then ok "git present";  else err "git not found (required to fetch kubernetes-goat)"; fail=1; fi

# Can we talk to the docker daemon?
if docker info >/dev/null 2>&1; then ok "docker daemon reachable"; else err "cannot reach docker daemon (need root or docker group)"; fail=1; fi

# --- Resources ---------------------------------------------------------------
avail=$(free_mb)
if [ "$avail" -ge 4000 ]; then ok "RAM: ${avail}MB free (full range incl. k3s OK)"
elif [ "$avail" -ge 2500 ]; then warn "RAM: ${avail}MB free — enough for web/net labs; k3s gate is 2500MB"
else warn "RAM: ${avail}MB free — LOW; deploy web labs only, skip k3s (or add swap)"; softfail=1; fi

disk=$(df -Pm "$BENCH_ROOT" | awk 'NR==2{print $4}')
if [ "$disk" -ge 15000 ]; then ok "disk: ${disk}MB free under $BENCH_ROOT"
else warn "disk: only ${disk}MB free — images may not fit (need ~15GB for full range)"; softfail=1; fi

# --- Ports (loopback publish targets) ---------------------------------------
for p in 8101 8102 8103 8104 8105 8106 8107; do
  if probe_tcp 127.0.0.1 "$p" | grep -q open; then warn "port $p already in use on 127.0.0.1"; softfail=1; fi
done
if probe_tcp 127.0.0.1 80 | grep -q open; then ok "something already listens on :80 (nginx?) — good"; else warn ":80 free — nginx not yet running (install-nginx.sh will need it)"; fi

# --- Optional (k3s / KVM full-parity paths) ---------------------------------
if have k3s || have kubectl; then ok "k3s/kubectl present"; else warn "k3s not installed — k8s/k3s-install.sh will install it"; fi
if have virsh; then ok "libvirt present (KVM MS3 best-effort path available)"; else warn "libvirt/virsh absent — KVM MS3 unavailable; MS3-lite container is the working path"; fi
if have python3; then ok "python3 present (needed for cloud venv: awslocal/checkov)"; else warn "python3 absent — cloud seed/iac-scan need it"; softfail=1; fi

echo
if [ "$fail" -ne 0 ]; then err "preflight FAILED — install the missing required tools above."; exit 1; fi
if [ "$softfail" -ne 0 ]; then warn "preflight passed with warnings (see above)."; else ok "preflight passed cleanly."; fi
exit 0
