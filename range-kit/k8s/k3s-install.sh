#!/usr/bin/env bash
# Install a single-node k3s cluster (the substrate for Kubernetes Goat).
# Idempotent — skips if k3s is already serving. Requires root + outbound network.
source "$(dirname "${BASH_SOURCE[0]}")/../bin/lib.sh"

[ "$(id -u)" -eq 0 ] || die "must run as root to install k3s"

if have kubectl && kubectl get nodes >/dev/null 2>&1; then
  ok "k3s/kubectl already serving:"; kubectl get nodes | sed 's/^/    /'; exit 0
fi

log "installing k3s (get.k3s.io)"
# --write-kubeconfig-mode 644 so non-root tooling (checkov, port-forward) can read it.
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--write-kubeconfig-mode 644" sh - \
  || die "k3s install failed"

# Make kubectl config discoverable.
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
log "waiting for node Ready..."
for i in $(seq 1 30); do
  kubectl get nodes 2>/dev/null | grep -q ' Ready ' && break || sleep 4
done
kubectl get nodes | sed 's/^/    /'
ok "k3s installed. Export KUBECONFIG=/etc/rancher/k3s/k3s.yaml for kubectl."
