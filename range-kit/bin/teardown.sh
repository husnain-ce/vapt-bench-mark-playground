#!/usr/bin/env bash
# Tear the range down to free RAM. By default stops containers + port-forward and
# leaves images/volumes/k3s in place for a fast re-up. Flags go further:
#
#   --k8s        also uninstall Kubernetes Goat workloads (keeps k3s running)
#   --k3s        also uninstall the whole k3s cluster (k3s-uninstall.sh)
#   --purge      also remove the aqira-range network + named volumes + venv
#   --all        --k3s + --purge
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

DO_K8S=0; DO_K3S=0; DO_PURGE=0
for a in "$@"; do case "$a" in
  --k8s) DO_K8S=1 ;;
  --k3s) DO_K3S=1; DO_K8S=1 ;;
  --purge) DO_PURGE=1 ;;
  --all) DO_K3S=1; DO_K8S=1; DO_PURGE=1 ;;
  *) die "unknown flag: $a" ;;
esac; done

# 1. compose stacks
for f in weblab-juice weblab-dvwa apilab-webgoat apilab-vampi weblab-log4shell \
         cloud-localstack netlab-ms2 netlab-ms3; do
  [ -f "$COMPOSE_DIR/$f.yml" ] || continue
  log "down: $f"
  dc -f "$COMPOSE_DIR/$f.yml" down 2>/dev/null || true
done
ok "compose stacks stopped"

# 2. k8s port-forward
"$K8S_DIR/portforward.sh" stop 2>/dev/null || true

# 3. Kubernetes Goat workloads
if [ "$DO_K8S" = 1 ] && have kubectl; then
  export KUBECONFIG="${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}"
  if [ -f "$K8S_DIR/kubernetes-goat/teardown-kubernetes-goat.sh" ]; then
    log "tearing down Kubernetes Goat workloads"
    ( cd "$K8S_DIR/kubernetes-goat" && bash teardown-kubernetes-goat.sh ) 2>/dev/null || true
  fi
fi

# 4. k3s cluster
if [ "$DO_K3S" = 1 ]; then
  if [ -x /usr/local/bin/k3s-uninstall.sh ]; then
    log "uninstalling k3s cluster"; /usr/local/bin/k3s-uninstall.sh || true
  else warn "k3s-uninstall.sh not found; skipping"; fi
fi

# 5. purge network/volumes/venv
if [ "$DO_PURGE" = 1 ]; then
  log "purging network + volumes + venv"
  docker network rm "$RANGE_NET" 2>/dev/null || true
  docker volume rm localstack-data 2>/dev/null || true
  rm -rf "$RANGE_VENV"
  ok "purged"
fi

echo; ok "teardown done. Free RAM now: $(free_mb)MB"
