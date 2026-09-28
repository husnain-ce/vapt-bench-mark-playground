#!/usr/bin/env bash
# Manage the kubectl port-forward that exposes Kubernetes Goat on 127.0.0.1:8106
# (nginx fronts it as k8sgoat.range.example.com). k3s port-forwards die on pod
# restarts, so this wraps start/stop/status with a pidfile and a keepalive loop.
#
# Usage: portforward.sh {start|stop|status}
source "$(dirname "${BASH_SOURCE[0]}")/../bin/lib.sh"

export KUBECONFIG="${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}"
PIDFILE="/run/aqira-k8sgoat-pf.pid"
[ -w /run ] || PIDFILE="$BENCH_ROOT/.k8sgoat-pf.pid"
PORT=8106
# The main Kubernetes Goat landing app. Adjust if upstream renames the service.
SVC="${K8SGOAT_SVC:-svc/kubernetes-goat-home-service}"

start() {
  if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    ok "port-forward already running (pid $(cat "$PIDFILE"))"; return 0
  fi
  have kubectl || die "kubectl not found"
  log "starting keepalive port-forward $SVC -> 127.0.0.1:$PORT"
  # Keepalive loop: restart the forward whenever it drops.
  nohup bash -c "
    export KUBECONFIG='$KUBECONFIG'
    while true; do
      kubectl port-forward --address 127.0.0.1 $SVC $PORT:80 >/dev/null 2>&1 || \
      kubectl port-forward --address 127.0.0.1 $SVC $PORT:8080 >/dev/null 2>&1
      sleep 5
    done
  " >/dev/null 2>&1 &
  echo $! > "$PIDFILE"
  ok "port-forward keepalive started (pid $(cat "$PIDFILE"))"
}

stop() {
  if [ -f "$PIDFILE" ]; then
    kill "$(cat "$PIDFILE")" 2>/dev/null && ok "stopped port-forward" || warn "no live process"
    rm -f "$PIDFILE"
  else
    warn "no pidfile; nothing to stop"
  fi
  pkill -f "port-forward.*$PORT:" 2>/dev/null || true
}

status() {
  if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    ok "running (pid $(cat "$PIDFILE")); probe: $(probe_tcp 127.0.0.1 $PORT)"
  else
    warn "not running"
  fi
}

case "${1:-status}" in
  start) start ;;
  stop)  stop ;;
  status) status ;;
  *) die "usage: $0 {start|stop|status}" ;;
esac
