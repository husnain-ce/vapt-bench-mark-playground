#!/usr/bin/env bash
# Install the range /etc/hosts block idempotently (replaces the marked block).
# Requires root (writes /etc/hosts).
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

[ "$(id -u)" -eq 0 ] || die "must run as root to edit /etc/hosts"

SRC="$HOSTS_DIR/aqira-range.hosts"
[ -f "$SRC" ] || die "missing $SRC"

BEGIN="# >>> aqira-range >>>"
END="# <<< aqira-range <<<"

# Strip any existing block, then append the fresh one.
tmp="$(mktemp)"
awk -v b="$BEGIN" -v e="$END" '
  $0==b {skip=1}
  skip==0 {print}
  $0==e {skip=0}
' /etc/hosts > "$tmp"

cat "$SRC" >> "$tmp"
# Collapse any trailing blank lines to one.
install -m 644 "$tmp" /etc/hosts
rm -f "$tmp"
ok "/etc/hosts updated with the aqira-range block"
grep -c 'range.example.com' /etc/hosts >/dev/null && log "$(grep -c 'range.example.com' /etc/hosts) range host lines present"
