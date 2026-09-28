#!/usr/bin/env bash
# Install the range reverse-proxy vhosts into the system nginx and reload.
# Requires root + a system nginx that includes /etc/nginx/conf.d/*.conf.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

[ "$(id -u)" -eq 0 ] || die "must run as root to install nginx config"
have nginx || die "nginx not installed. apt-get install -y nginx (or skip: reach labs by 127.0.0.1:<port>)"

CONF_D="/etc/nginx/conf.d"
mkdir -p "$CONF_D"
install -m 644 "$NGINX_DIR/aqira-range.conf"       "$CONF_D/aqira-range.conf"
install -m 644 "$NGINX_DIR/aqira-range-proxy.inc"  "$CONF_D/aqira-range-proxy.inc"
ok "installed aqira-range.conf + aqira-range-proxy.inc into $CONF_D"

log "nginx -t"
if nginx -t 2>&1 | sed 's/^/    /'; then
  systemctl reload nginx 2>/dev/null || nginx -s reload
  ok "nginx reloaded"
else
  die "nginx config test failed — not reloading"
fi
