#!/usr/bin/env bash
# Patiently pull the Kubernetes Goat scenario images and import them into the
# k3s containerd image store (single stream each, retried). Avoids the flaky
# in-cluster ImagePullBackOff seen on slow links. Best-effort; never fatal.
source "$(dirname "${BASH_SOURCE[0]}")/../bin/lib.sh"

K3S_BIN="$(command -v k3s || echo /usr/local/bin/k3s)"
imgs="madhuakula/k8s-goat-hidden-in-layers madhuakula/k8s-goat-system-monitor busybox:latest madhuakula/k8s-goat-health-check madhuakula/k8s-goat-info-app madhuakula/k8s-goat-poddelete madhuakula/k8s-goat-batch-check madhuakula/k8s-goat-build-code madhuakula/k8s-goat-metadata-db"

for img in $imgs; do
  base="$(echo "$img" | sed 's/:.*//')"
  if "$K3S_BIN" ctr images ls 2>/dev/null | grep -q "$base"; then
    ok "present: $img"; continue
  fi
  for attempt in 1 2 3 4 5; do
    log "pull attempt $attempt: $img"
    if docker pull "$img" >/dev/null 2>&1; then
      docker save "$img" | "$K3S_BIN" ctr images import - >/dev/null 2>&1 && { ok "imported: $img"; break; }
    fi
    sleep 15
  done
done
log "imported goat images:"
"$K3S_BIN" ctr images ls 2>/dev/null | grep -oE 'k8s-goat-[a-z-]+|busybox' | sort -u | tr '\n' ' '; echo
