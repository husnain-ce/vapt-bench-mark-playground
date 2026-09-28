#!/bin/bash
# MS3-lite (Ubuntu 14.04) — start the vulnerable service set, keep PID 1 alive.
set -e

# SSH host keys (generated at first boot, not baked into the image).
[ -f /etc/ssh/ssh_host_rsa_key ] || dpkg-reconfigure openssh-server >/dev/null 2>&1 || ssh-keygen -A

service apache2 start   || /usr/sbin/apache2ctl start || true
service ssh start       || /usr/sbin/sshd || true
# Source-built (vulnerable) proftpd 1.3.5, standalone/backgrounded.
/usr/local/proftpd/sbin/proftpd -c /usr/local/proftpd/etc/proftpd.conf || true

echo "[ms3-lite] services up: ftp(21, proftpd-1.3.5 mod_copy CVE-2015-3306) ssh(22, vagrant/vagrant) http(80)"
# Hold the container open and surface apache logs.
tail -F /var/log/apache2/access.log 2>/dev/null &
exec sleep infinity
