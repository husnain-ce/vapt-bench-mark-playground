# Aqira Cyber Range - Agent A - Metasploitable 3 (Ubuntu 14.04) *Docker-fallback*
#
# WHY A FALLBACK (see deploy.md): the supplied vagrant box
#   /home/aqsec/aqira-range/vm/ms3-ub1404.box
# is (a) a *virtualbox*-provider box (vmdk inside an OVF, not a libvirt qcow2)
# and (b) a TRUNCATED download -- `gzip -t` reports "unexpected end of file" and
# the extracted vmdk fails `qemu-img info` with "Invalid footer". With no
# vagrant/packer installed to rebuild it and only ~2 GB RAM free (live Aqira
# scans running), a 4 GB-default KVM VM was not viable. This image reproduces the
# classic MS3-ub1404 *Ubuntu 14.04* vulnerable service surface in a ~90 MB
# container instead: ProFTPd 1.3.5 mod_copy (CVE-2015-3306), OpenSSH weak creds
# (vagrant/vagrant), a PHP command-injection app, and a UNION-based SQLi login.
FROM ubuntu:14.04

# NOTE: archive.ubuntu.com + security.ubuntu.com still serve trusty (verified
# 200 OK), so the base image's default sources.list is used as-is. (old-releases
# does NOT host trusty and 404s — do not rewrite the mirrors.)
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      apache2 php5 libapache2-mod-php5 \
      openssh-server \
      sudo net-tools iproute2 sqlite3 php5-sqlite \
      build-essential wget ca-certificates \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- OpenSSH: weak creds, the signature MS3-ub1404 credential (vagrant/vagrant)
RUN mkdir -p /var/run/sshd \
 && useradd -m -s /bin/bash vagrant \
 && echo 'vagrant:vagrant' | chpasswd \
 && adduser vagrant sudo \
 && echo 'root:vagrant' | chpasswd \
 && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config \
 && sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

# --- ProFTPd 1.3.5 (GENUINE VULNERABLE build from source) = CVE-2015-3306.
# The Ubuntu 14.04 distro package (proftpd-basic, 1.3.5rc3) is *patched* — its
# mod_copy rejects SITE CPFR pre-auth ("requires authentication"), so the CVE is
# not reproducible from it. We compile stock proftpd-1.3.5 with mod_copy statically
# linked; in this release mod_copy's SITE CPFR/CPTO are reachable UN-authenticated
# (fixed only in 1.3.5a), which is exactly the primitive metasploit's
# proftpd_modcopy_exec abuses to plant a PHP payload into the Apache DocumentRoot.
RUN cd /usr/src \
 && wget -q ftp://ftp.proftpd.org/distrib/source/proftpd-1.3.5.tar.gz \
 && tar xzf proftpd-1.3.5.tar.gz && cd proftpd-1.3.5 \
 && ./configure --prefix=/usr/local/proftpd --sysconfdir=/usr/local/proftpd/etc \
      --localstatedir=/usr/local/proftpd/var --with-modules=mod_copy >/dev/null \
 && make -j"$(nproc)" >/dev/null && make install >/dev/null \
 && cd /usr/src && rm -rf proftpd-1.3.5 proftpd-1.3.5.tar.gz
COPY proftpd.conf /usr/local/proftpd/etc/proftpd.conf

# Writable state dir for the sqlite-backed portal app (login.php).
RUN mkdir -p /var/lib/ms3app && chown www-data:www-data /var/lib/ms3app && chmod 0777 /var/lib/ms3app

# --- Apache web root: make it writable by www-data so mod_copy can plant .php
COPY webroot/ /var/www/html/
RUN chown -R www-data:www-data /var/www/html && chmod -R 0777 /var/www/html \
 && a2enmod php5 2>/dev/null || true

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 21 ftp, 22 ssh, 80 http  (EXPOSE is documentation only; compose does NOT
# publish these to the host -- reachable only on the aqira-range network.)
EXPOSE 21 22 80
CMD ["/entrypoint.sh"]
