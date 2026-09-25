import shlex


def bootstrap_script(config, mappings):
    machine = config["machine"]
    download = machine["download"]
    disk = machine["disk"]
    vm = machine.get("vm", {})

    url = download["url"]
    name = download["archive_name"]
    sha256 = download["sha256"].lower()
    disk_format = disk.get("format", "vmdk")
    disk_glob = disk.get("search_glob", "*.vmdk")
    memory_mb = int(vm.get("memory_mb", 768))
    vcpus = int(vm.get("vcpus", 1))
    nic_model = vm.get("nic_model", "e1000")

    hostfwds = [
        f"hostfwd={m['protocol']}:0.0.0.0:{m['external']}-:{m['guest']}"
        for m in mappings
    ]
    netdev = ",".join(["user", "id=n1"] + hostfwds)

    return f"""set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

echo "[MACHINE 1/8] Starting remote installation"
date -Is
echo "[MACHINE 2/8] Updating Ubuntu package lists..."
apt-get update

echo "[MACHINE 3/8] Installing QEMU/KVM dependencies..."
apt-get install -y qemu-system-x86 qemu-utils unzip curl ca-certificates
echo "[MACHINE 3/8] Dependencies installed."

echo "[MACHINE 4/8] Checking nested virtualization..."
if [ ! -e /dev/kvm ]; then
  echo "ERROR: /dev/kvm is missing. Nested virtualization is unavailable." >&2
  exit 30
fi
ls -l /dev/kvm

mkdir -p /opt/aqsec/machine
cd /opt/aqsec/machine

echo "[MACHINE 5/8] Download URL: {url}"
rm -f {shlex.quote(name)}
curl -fL --progress-bar --retry 5 --retry-delay 3 \
  -o {shlex.quote(name)} {shlex.quote(url)}

echo "[MACHINE 6/8] Verifying SHA-256..."
ACTUAL_SHA256="$(sha256sum {shlex.quote(name)} | awk '{{print tolower($1)}}')"
echo "[MACHINE] SHA256: $ACTUAL_SHA256"

if [ "$ACTUAL_SHA256" != "{sha256}" ]; then
  echo "SHA256 mismatch." >&2
  echo "Expected: {sha256}" >&2
  echo "Actual:   $ACTUAL_SHA256" >&2
  exit 21
fi

echo "[MACHINE] Checksum OK."
echo "[MACHINE 7/8] Extracting archive..."
rm -rf extracted
mkdir extracted
unzip -q {shlex.quote(name)} -d extracted

DISK="$(find extracted -type f -iname {shlex.quote(disk_glob)} | head -n1)"
if [ -z "$DISK" ]; then
  echo "ERROR: No disk matching {disk_glob} found." >&2
  exit 22
fi

echo "[MACHINE] Disk: $DISK"

cat >/etc/systemd/system/aqsec-vulnerable-machine.service <<UNIT
[Unit]
Description=AQSEC vulnerable benchmark VM
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/aqsec/machine
ExecStart=/usr/bin/qemu-system-i386 \\
  -name aqsec-vulnerable-machine \\
  -machine accel=kvm \\
  -m {memory_mb} \\
  -smp {vcpus} \\
  -drive file=$DISK,format={disk_format},if=ide \\
  -netdev {netdev} \\
  -device {nic_model},netdev=n1 \\
  -nographic \\
  -no-reboot
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

echo "[MACHINE 8/8] Starting VM..."
systemctl daemon-reload
systemctl enable aqsec-vulnerable-machine.service
systemctl restart aqsec-vulnerable-machine.service
sleep 8

echo "[MACHINE] Service status:"
systemctl --no-pager --full status aqsec-vulnerable-machine.service || true

if ! systemctl is-active --quiet aqsec-vulnerable-machine.service; then
  echo "ERROR: vulnerable machine QEMU service is not active." >&2
  journalctl -u aqsec-vulnerable-machine.service --no-pager -n 100 >&2 || true
  exit 40
fi

echo "[MACHINE] QEMU listeners:"
ss -lntup | grep qemu || true
echo "[MACHINE] VM service is active."
date -Is
"""
