#!/usr/bin/env bash
# Shared helpers for the Aqira Benchmark deployment kit.
# Source this from every bin/ and cloud/ script:  source "$(dirname "$0")/lib.sh"
#
# Establishes the canonical paths and small utilities (logging, RAM gate,
# HTTP probe) so every script agrees on where the range lives.

set -uo pipefail

# --- Canonical locations -----------------------------------------------------
# BENCH_ROOT is the kit's own directory (this file lives in $BENCH_ROOT/bin).
BENCH_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export BENCH_ROOT
export COMPOSE_DIR="$BENCH_ROOT/compose"
export CLOUD_DIR="$BENCH_ROOT/cloud"
export K8S_DIR="$BENCH_ROOT/k8s"
export VM_DIR="$BENCH_ROOT/vm"
export NGINX_DIR="$BENCH_ROOT/nginx"
export HOSTS_DIR="$BENCH_ROOT/hosts"
export EVIDENCE_DIR="$BENCH_ROOT/evidence"
export RANGE_VENV="$BENCH_ROOT/.venv"

# --- Network model (must match manifest.yaml + compose/hosts) ----------------
export RANGE_NET="aqira-range"
export RANGE_SUBNET="172.30.0.0/24"
export RANGE_GATEWAY="172.30.0.1"

# --- Domains fronted by nginx (loopback web labs) ----------------------------
export RANGE_DOMAIN_SUFFIX="range.example.com"

# --- Logging -----------------------------------------------------------------
_c() { printf '\033[%sm' "$1"; }   # color helper; no-op if not a tty
if [ -t 1 ]; then C_RED=$(_c 31); C_GRN=$(_c 32); C_YEL=$(_c 33); C_BLU=$(_c 36); C_OFF=$(_c 0)
else C_RED=; C_GRN=; C_YEL=; C_BLU=; C_OFF=; fi
log()   { printf '%s[bench]%s %s\n' "$C_BLU" "$C_OFF" "$*"; }
ok()    { printf '%s[ ok ]%s %s\n' "$C_GRN" "$C_OFF" "$*"; }
warn()  { printf '%s[warn]%s %s\n' "$C_YEL" "$C_OFF" "$*"; }
err()   { printf '%s[fail]%s %s\n' "$C_RED" "$C_OFF" "$*" >&2; }
die()   { err "$*"; exit 1; }

# --- Utilities ---------------------------------------------------------------
have() { command -v "$1" >/dev/null 2>&1; }

# docker compose OR docker-compose, whichever exists
dc() {
  if docker compose version >/dev/null 2>&1; then docker compose "$@"
  elif have docker-compose; then docker-compose "$@"
  else die "neither 'docker compose' nor 'docker-compose' is installed"; fi
}

# free RAM in MB
free_mb() { free -m | awk '/^Mem:/ {print $7}'; }

# Refuse to proceed unless at least $1 MB is available. Honors FORCE=1 override.
require_ram() {
  local need="$1" avail; avail=$(free_mb)
  if [ "$avail" -lt "$need" ]; then
    if [ "${FORCE:-0}" = "1" ]; then
      warn "only ${avail}MB free (< ${need}MB) but FORCE=1 set — proceeding"
    else
      die "only ${avail}MB free; need >= ${need}MB. Free RAM or re-run with FORCE=1."
    fi
  else
    ok "RAM check: ${avail}MB free (>= ${need}MB)"
  fi
}

# HTTP probe by Host header against local nginx; prints status code.
probe_http() {
  local host="$1" path="${2:-/}"
  curl -s -o /dev/null -w '%{http_code}' -H "Host: ${host}" "http://127.0.0.1${path}" 2>/dev/null || echo "000"
}

# TCP probe: probe_tcp <ip> <port>
probe_tcp() {
  local ip="$1" port="$2"
  timeout 3 bash -c "cat < /dev/null > /dev/tcp/${ip}/${port}" 2>/dev/null && echo "open" || echo "closed"
}
