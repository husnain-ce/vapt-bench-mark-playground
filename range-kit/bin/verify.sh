#!/usr/bin/env bash
# Health-probe every lab in the range and print a pass/fail table.
# Web/API/cloud labs are probed through nginx by Host header; network labs by
# TCP to their bridge IP. Exit 0 only if every non-optional lab is reachable.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

pass=0; fail=0
printf '%-12s %-34s %-8s %s\n' "LAB" "TARGET" "RESULT" "DETAIL"
printf '%.0s-' {1..78}; echo

check_http() { # id host path
  local id="$1" host="$2" path="${3:-/}" code
  code=$(probe_http "$host" "$path")
  if [[ "$code" =~ ^(200|301|302|401|403)$ ]]; then
    printf '%-12s %-34s %s%-8s%s HTTP %s\n' "$id" "$host$path" "$C_GRN" "PASS" "$C_OFF" "$code"; pass=$((pass+1))
  else
    printf '%-12s %-34s %s%-8s%s HTTP %s\n' "$id" "$host$path" "$C_RED" "FAIL" "$C_OFF" "$code"; fail=$((fail+1))
  fi
}
check_tcp() { # id ip port
  local id="$1" ip="$2" port="$3" st
  st=$(probe_tcp "$ip" "$port")
  if [ "$st" = "open" ]; then
    printf '%-12s %-34s %s%-8s%s tcp/%s\n' "$id" "$ip:$port" "$C_GRN" "PASS" "$C_OFF" "$port"; pass=$((pass+1))
  else
    printf '%-12s %-34s %s%-8s%s tcp/%s\n' "$id" "$ip:$port" "$C_RED" "FAIL" "$C_OFF" "$port"; fail=$((fail+1))
  fi
}

check_http juice      juice.range.example.com      /
check_http dvwa       dvwa.range.example.com       /login.php
check_http webgoat    webgoat.range.example.com    /WebGoat
check_http vampi      vampi.range.example.com      /
check_http log4shell  log4shell.range.example.com  /solr/
check_http k8sgoat    k8sgoat.range.example.com    /
check_http localstack localstack.range.example.com /_localstack/health
check_tcp  ms2        172.30.0.11                  22
check_tcp  ms3        172.30.0.12                  21

echo
if [ "$fail" -eq 0 ]; then ok "all $pass labs reachable"; exit 0
else warn "$pass reachable, $fail unreachable (heavy labs may still be starting; re-run)"; exit 1; fi
