#!/usr/bin/env bash
# Deploy Kubernetes Goat onto the local k3s cluster.
#   1. ensure k3s is up (k3s-install.sh)
#   2. fetch kubernetes-goat (pinned ref) into ./kubernetes-goat
#   3. pre-pull the scenario images into containerd (avoids flaky in-cluster pulls)
#   4. run the upstream setup-kubernetes-goat.sh
#   5. expose the main app on 127.0.0.1:8106 via kubectl port-forward (portforward.sh)
#
# RAM gate: k3s + goat pods want ~2.5 GB headroom. Override with FORCE=1.
source "$(dirname "${BASH_SOURCE[0]}")/../bin/lib.sh"

require_ram 2500

K8SGOAT_REPO="${K8SGOAT_REPO:-https://github.com/madhuakula/kubernetes-goat.git}"
K8SGOAT_REF="${K8SGOAT_REF:-master}"   # pin to a tag/commit for full reproducibility
DEST="$K8S_DIR/kubernetes-goat"

# 1. k3s
"$K8S_DIR/k3s-install.sh"
export KUBECONFIG="${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}"
have kubectl || die "kubectl not on PATH after k3s install"

# 2. fetch kubernetes-goat
if [ -d "$DEST/.git" ] || [ -f "$DEST/setup-kubernetes-goat.sh" ]; then
  ok "kubernetes-goat already present at $DEST"
else
  log "cloning kubernetes-goat ($K8SGOAT_REF)"
  git clone --depth 1 --branch "$K8SGOAT_REF" "$K8SGOAT_REPO" "$DEST" 2>/dev/null \
    || git clone "$K8SGOAT_REPO" "$DEST"   # fallback: ref may be a commit, not a branch
fi

# 3. pre-pull scenario images into k3s containerd (best-effort, retried)
if [ -x "$K8S_DIR/pull-images.sh" ]; then
  log "pre-pulling scenario images into containerd"
  "$K8S_DIR/pull-images.sh" || warn "some images failed to pre-pull; k3s will retry in-cluster"
fi

# 4. run upstream setup
log "running upstream setup-kubernetes-goat.sh"
( cd "$DEST" && bash setup-kubernetes-goat.sh ) || warn "setup reported errors; check 'kubectl get pods'"

log "current goat pods:"
kubectl get pods 2>/dev/null | sed 's/^/    /'

# 5. expose on 8106
"$K8S_DIR/portforward.sh" start || warn "port-forward not started; run k8s/portforward.sh start manually"
ok "Kubernetes Goat deployed (k8sgoat.range.example.com -> 127.0.0.1:8106)"
