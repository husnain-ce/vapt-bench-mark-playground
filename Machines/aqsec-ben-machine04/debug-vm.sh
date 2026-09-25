#!/usr/bin/env bash
set -u

echo "=== QEMU service ==="
sudo systemctl --no-pager --full status aqsec-vulnerable-machine.service || true

echo
echo "=== QEMU listeners ==="
sudo ss -lntup | grep qemu || true

echo
echo "=== HTTP tests ==="
for p in 80 10000 20000; do
  echo "--- port $p ---"
  curl -v --connect-timeout 3 --max-time 8 "http://127.0.0.1:$p/" || true
done

echo
echo "=== Recent QEMU journal ==="
sudo journalctl -u aqsec-vulnerable-machine.service --no-pager -n 250
