import shlex


def _extract_script(archive_type: str, nested_type: str | None, archive_name: str) -> str:
    q = shlex.quote(archive_name)

    if archive_type == "zip" and nested_type == "ova":
        return f"""
echo "[MACHINE] Extracting ZIP..."
set +e
unzip -o {q} -d extracted
UNZIP_RC="$?"
set -e
echo "[MACHINE] unzip exit code: $UNZIP_RC"
echo "[MACHINE] Extracted files:"
find extracted -maxdepth 6 -type f || true

# unzip exit code 1 can be warning. Fatal is >1.
if [ "$UNZIP_RC" -gt 1 ]; then
  echo "ERROR: unzip failed with fatal exit code $UNZIP_RC" >&2
  exit "$UNZIP_RC"
fi

OVA="$(find extracted -type f -iname '*.ova' | head -n1)"
if [ -z "$OVA" ]; then
  echo "[MACHINE] No nested OVA found. Continuing with direct extracted files."
else
  echo "[MACHINE] Nested OVA: $OVA"
  mkdir -p extracted_ova
  tar -xf "$OVA" -C extracted_ova
fi
"""

    if archive_type == "zip":
        return f"""
echo "[MACHINE] Extracting ZIP..."
set +e
unzip -o {q} -d extracted
UNZIP_RC="$?"
set -e
echo "[MACHINE] unzip exit code: $UNZIP_RC"
echo "[MACHINE] Extracted files:"
find extracted -maxdepth 6 -type f || true

# unzip exit code 1 can be warning. Fatal is >1.
if [ "$UNZIP_RC" -gt 1 ]; then
  echo "ERROR: unzip failed with fatal exit code $UNZIP_RC" >&2
  exit "$UNZIP_RC"
fi
"""

    if archive_type == "ova":
        return f"""
echo "[MACHINE] Extracting OVA..."
tar -xf {q} -C extracted
echo "[MACHINE] Extracted files:"
find extracted -maxdepth 6 -type f || true
"""

    raise RuntimeError(f"Unsupported archive type: {archive_type}")


def bootstrap_script(config, mappings):
    machine = config["machine"]
    machine_label = machine.get("id") or machine.get("name") or "aqsec-ben-machine06"
    download = machine["download"]
    disk = machine["disk"]
    vm = machine.get("vm", {})
    archive = machine.get("archive", {})
    readiness = machine.get("readiness", {})

    url = download["url"]
    archive_name = download["archive_name"]
    md5 = download.get("md5")
    sha1 = download.get("sha1")
    sha256 = download.get("sha256")

    archive_type = archive.get("type", "zip").lower()
    nested_type = archive.get("nested_type")
    nested_type = nested_type.lower() if nested_type else None

    source_format = disk.get("source_format", disk.get("format", "vmdk"))
    disk_glob = disk.get("search_glob", "*.vmdk")
    runtime_format = disk.get("runtime_format", source_format)
    runtime_name = disk.get("runtime_name", f"disk.{runtime_format}")
    convert_to_runtime = bool(disk.get("convert_to_runtime", source_format != runtime_format))

    arch = vm.get("architecture", "x86_64")
    if arch == "x86_64":
        qemu_binary = "/usr/bin/qemu-system-x86_64"
    elif arch == "i386":
        qemu_binary = "/usr/bin/qemu-system-i386"
    else:
        raise RuntimeError(f"Unsupported architecture: {arch}")

    acceleration = vm.get("acceleration", "auto")
    memory_mb = int(vm.get("memory_mb", 1024))
    vcpus = int(vm.get("vcpus", 1))
    nic_model = vm.get("nic_model", "e1000")

    hostfwds = [
        f"hostfwd={m['protocol']}:0.0.0.0:{m['external']}-:{m['guest']}"
        for m in mappings
    ]
    netdev = ",".join(["user", "id=n1"] + hostfwds)

    qname = shlex.quote(archive_name)
    checksum_lines = []

    if md5:
        checksum_lines.append(f"""
ACTUAL_MD5="$(md5sum {qname} | awk '{{print toupper($1)}}')"
echo "[MACHINE] MD5: $ACTUAL_MD5"
if [ "$ACTUAL_MD5" != "{md5.upper()}" ]; then
  echo "MD5 mismatch. Expected {md5.upper()}, got $ACTUAL_MD5" >&2
  exit 21
fi
""")

    if sha1:
        checksum_lines.append(f"""
ACTUAL_SHA1="$(sha1sum {qname} | awk '{{print toupper($1)}}')"
echo "[MACHINE] SHA1: $ACTUAL_SHA1"
if [ "$ACTUAL_SHA1" != "{sha1.upper()}" ]; then
  echo "SHA1 mismatch. Expected {sha1.upper()}, got $ACTUAL_SHA1" >&2
  exit 21
fi
""")

    if sha256:
        checksum_lines.append(f"""
ACTUAL_SHA256="$(sha256sum {qname} | awk '{{print tolower($1)}}')"
echo "[MACHINE] SHA256: $ACTUAL_SHA256"
if [ "$ACTUAL_SHA256" != "{sha256.lower()}" ]; then
  echo "SHA256 mismatch. Expected {sha256.lower()}, got $ACTUAL_SHA256" >&2
  exit 21
fi
""")

    if checksum_lines:
        checksum_block = 'echo "[MACHINE 6/10] Verifying checksum(s)..."\n' + "\n".join(checksum_lines) + '\necho "[MACHINE] Checksum verification OK."\n'
    else:
        checksum_block = 'echo "[MACHINE 6/10] No checksum configured; skipping verification."\n'

    guest_to_external = {(int(m["guest"]), m["protocol"]): int(m["external"]) for m in mappings}
    probes = readiness.get("probes", [])
    boot_wait = int(readiness.get("boot_wait_seconds", 90))
    ready_timeout = int(readiness.get("timeout_seconds", 900))
    interval = int(readiness.get("interval_seconds", 10))

    probe_scripts = []
    conditions = []

    for idx, probe in enumerate(probes):
        typ = probe.get("type")
        guest_port = int(probe["external_port_for_guest"])
        external = guest_to_external.get((guest_port, "tcp"))
        if not external:
            continue

        var = f"READY_{idx}"
        conditions.append(f'[ "${{{var}:-0}}" -eq 1 ]')

        if typ == "http":
            probe_scripts.append(f"""
{var}=0
if curl -fsS --connect-timeout 3 --max-time 8 "http://127.0.0.1:{external}/" >/tmp/aqsec-probe-{idx}.out 2>/tmp/aqsec-probe-{idx}.err; then
  echo "[READY] HTTP guest:{guest_port} -> host:{external} responded."
  {var}=1
fi
""")
        elif typ == "tcp":
            probe_scripts.append(f"""
{var}=0
if timeout 4 bash -c 'cat < /dev/null > /dev/tcp/127.0.0.1/{external}' 2>/dev/null; then
  echo "[READY] TCP guest:{guest_port} -> host:{external} accepted connection."
  {var}=1
fi
""")
        elif typ == "ssh_banner":
            probe_scripts.append(f"""
{var}=0
SSH_BANNER="$(timeout 6 bash -c 'exec 3<>/dev/tcp/127.0.0.1/{external}; timeout 4 head -c 100 <&3' 2>/dev/null || true)"
if echo "$SSH_BANNER" | grep -q '^SSH-'; then
  echo "[READY] SSH guest:{guest_port} -> host:{external} banner: $SSH_BANNER"
  {var}=1
fi
""")

    if conditions:
        readiness_block = f"""
echo "[MACHINE 10/10] Waiting for guest service readiness..."
echo "[READY] Initial boot wait: {boot_wait}s"
sleep {boot_wait}
READY_START="$(date +%s)"

while true; do
  if ! systemctl is-active --quiet aqsec-ben-machine06.service; then
    echo "ERROR: QEMU exited while waiting for guest readiness." >&2
    journalctl -u aqsec-ben-machine06.service --no-pager -n 300 >&2 || true
    exit 41
  fi

  {"".join(probe_scripts)}

  if {" || ".join(conditions)}; then
    echo "[READY] At least one configured guest service is responding."
    break
  fi

  NOW="$(date +%s)"
  ELAPSED="$((NOW - READY_START))"

  if [ "$ELAPSED" -ge {ready_timeout} ]; then
    echo "ERROR: Guest readiness timed out after {ready_timeout}s." >&2
    echo "[DIAG] QEMU listeners:" >&2
    ss -lntup | grep qemu >&2 || true
    echo "[DIAG] QEMU journal:" >&2
    journalctl -u aqsec-ben-machine06.service --no-pager -n 300 >&2 || true
    exit 42
  fi

  echo "[READY] Guest still booting or service not ready... elapsed=${{ELAPSED}}s"
  sleep {interval}
done
"""
    else:
        readiness_block = 'echo "[MACHINE 10/10] No readiness probes configured."\n'

    extract_script = _extract_script(archive_type, nested_type, archive_name)

    if convert_to_runtime:
        disk_prep = f"""
echo "[MACHINE 8/10] Converting source disk to runtime format..."
echo "[MACHINE] Source disk: $DISK"
echo "[MACHINE] Runtime disk: /opt/aqsec/machine/{runtime_name}"
rm -f /opt/aqsec/machine/{runtime_name}
qemu-img convert -p -f {source_format} -O {runtime_format} "$DISK" /opt/aqsec/machine/{runtime_name}
qemu-img info /opt/aqsec/machine/{runtime_name}
DISK_FIXED="/opt/aqsec/machine/{runtime_name}"
RUNTIME_FORMAT="{runtime_format}"
"""
    else:
        disk_prep = f"""
echo "[MACHINE 8/10] Using source disk directly..."
rm -f /opt/aqsec/machine/disk.{source_format}
ln -s "$(realpath "$DISK")" /opt/aqsec/machine/disk.{source_format}
DISK_FIXED="/opt/aqsec/machine/disk.{source_format}"
RUNTIME_FORMAT="{source_format}"
qemu-img info "$DISK_FIXED" || true
"""

    return f"""set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

echo "[MACHINE 1/10] Starting generic vulnerable VM installation"
date -Is

echo "[MACHINE 2/10] Updating Ubuntu package lists..."
apt-get update

echo "[MACHINE 3/10] Installing dependencies..."
apt-get install -y qemu-system-x86 qemu-utils unzip curl ca-certificates tar
echo "[MACHINE 3/10] Dependencies installed."

echo "[MACHINE 4/10] Checking acceleration mode..."
ACCELERATION="{acceleration}"
if [ "$ACCELERATION" = "auto" ]; then
  if [ -e /dev/kvm ]; then
    ACCELERATION="kvm"
    CPU_MODEL="host"
  else
    ACCELERATION="tcg"
    CPU_MODEL="qemu64"
  fi
elif [ "$ACCELERATION" = "kvm" ]; then
  if [ ! -e /dev/kvm ]; then
    echo "ERROR: acceleration=kvm requested but /dev/kvm is missing." >&2
    exit 30
  fi
  CPU_MODEL="host"
else
  ACCELERATION="tcg"
  CPU_MODEL="qemu64"
fi
echo "[MACHINE] Acceleration: $ACCELERATION"
echo "[MACHINE] CPU model: $CPU_MODEL"
ls -l /dev/kvm 2>/dev/null || true

mkdir -p /opt/aqsec/machine
cd /opt/aqsec/machine

echo "[MACHINE 5/10] Downloading: {url}"
rm -f {qname}
curl -fL --progress-bar --retry 5 --retry-delay 3 -o {qname} {shlex.quote(url)}

{checksum_block}

echo "[MACHINE 7/10] Extracting archive..."
rm -rf extracted extracted_ova
mkdir -p extracted extracted_ova
{extract_script}

echo "[MACHINE] Searching for disk: {disk_glob}"
set +e
DISK="$(find extracted extracted_ova -type f -iname {shlex.quote(disk_glob)} 2>/dev/null | head -n1)"
FIND_RC="$?"
set -e
echo "[MACHINE] find disk exit code: $FIND_RC"
echo "[MACHINE] selected disk: ${{DISK:-NONE}}"
if [ -z "$DISK" ]; then
  echo "ERROR: No disk matching {disk_glob} found." >&2
  echo "[DIAG] Extracted files:" >&2
  find extracted extracted_ova -maxdepth 8 -type f >&2 2>/dev/null || true
  echo "[DIAG] Disk usage:" >&2
  df -h >&2 || true
  exit 22
fi

{disk_prep}

echo "[MACHINE] QEMU disk path: $DISK_FIXED"
echo "[MACHINE] QEMU disk format: $RUNTIME_FORMAT"

cat >/etc/systemd/system/aqsec-ben-machine06.service <<UNIT
[Unit]
Description=AQSEC benchmark VM {machine_label}
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/aqsec/machine
ExecStart={qemu_binary} \\
  -name {machine_label} \\
  -machine accel=$ACCELERATION \\
  -cpu $CPU_MODEL \\
  -m {memory_mb} \\
  -smp {vcpus} \\
  -drive file=$DISK_FIXED,format=$RUNTIME_FORMAT,if=ide \\
  -netdev {netdev} \\
  -device {nic_model},netdev=n1 \\
  -nographic \\
  -no-reboot
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

echo "[MACHINE 9/10] Starting VM..."
systemctl daemon-reload
systemctl enable aqsec-ben-machine06.service
systemctl restart aqsec-ben-machine06.service

sleep 5

if ! systemctl is-active --quiet aqsec-ben-machine06.service; then
  echo "ERROR: QEMU service failed." >&2
  journalctl -u aqsec-ben-machine06.service --no-pager -n 300 >&2 || true
  exit 40
fi

echo "[MACHINE] QEMU process is active."
echo "[MACHINE] QEMU listeners:"
ss -lntup | grep qemu || true

{readiness_block}

echo "[MACHINE] VM deployment complete."
date -Is
"""
