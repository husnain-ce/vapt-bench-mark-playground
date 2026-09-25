# AQSEC Generic AWS Vulnerable VM Deployer - Empire Breakout QCOW2 Final

This is the corrected package after testing Empire Breakout manually on Ubuntu EC2.

## Mistakes fixed from previous versions

1. **Wrong archive assumption**
   - Earlier: assumed `ZIP -> OVA -> VMDK`
   - Correct: Empire Breakout is `ZIP -> OVF + VMDK`

2. **Running streamOptimized VMDK directly**
   - Earlier: booted `Breakout-disk1.vmdk` directly
   - Problem: QEMU showed `Could not write to allocated cluster for streamOptimized`
   - Correct: convert VMDK to QCOW2 first

3. **KVM-only boot**
   - Earlier: forced `-machine accel=kvm -cpu host`
   - Problem: manual Ubuntu EC2 had no `/dev/kvm`
   - Correct: `acceleration: auto`
     - uses KVM if `/dev/kvm` exists
     - uses TCG + `qemu64` if KVM is missing

4. **Fragile remote port detection**
   - Earlier: SSH command for port detection timed out
   - Correct: do not run remote port detection
   - Preserve Ubuntu default ports: `22/tcp`, `53/tcp`, `53/udp`

5. **Install timeout**
   - Earlier: remote install could time out during large downloads/extraction
   - Correct: VM install command uses no fixed timeout

## Build

```bash
docker build --no-cache -t awsevil-qcow2-final .
```

## Run

```bash
docker run --rm -it awsevil-qcow2-final
```

## Expected important output

```text
[MACHINE] Acceleration: kvm
```

or if KVM is missing:

```text
[MACHINE] Acceleration: tcg
[MACHINE] CPU model: qemu64
```

Disk conversion:

```text
[MACHINE 8/10] Converting source disk to runtime format...
qemu-img convert -p -f vmdk -O qcow2 ...
[MACHINE] QEMU disk format: qcow2
```

## After success

From Kali:

```bash
nmap -Pn -sV -p 80,139,445,10000,20000 PUBLIC_IP
```

If Nmap shows `tcpwrapped` for a short time, wait. With TCG, boot can be slow.
With KVM, it should become ready much faster.

## Security reminder

Use `allowed_cidr: "auto"` or your scanner `/32`.
Do not expose vulnerable VMs globally.


## v2 fix: disk search with set -euo pipefail

The previous package failed after:

```text
[MACHINE] Searching for disk: *.vmdk
```

because `find extracted extracted_ova ...` returned a non-zero exit code when
`extracted_ova` did not exist or was empty. With `set -euo pipefail`, that
stopped the installer before it could select `Breakout-disk1.vmdk`.

This v2 package always creates `extracted_ova` and wraps the disk search with
`set +e` / `set -e`, then prints:

```text
[MACHINE] find disk exit code: ...
[MACHINE] selected disk: ...
```


## v3 fix: Python f-string shell variable bug

The v2 package had this line in the generated shell script:

```bash
echo "[MACHINE] selected disk: ${DISK:-NONE}"
```

Because it was inside a Python f-string, Python tried to evaluate `DISK` as a
Python variable and failed with:

```text
NameError: name 'DISK' is not defined
```

v3 escapes the braces correctly and was tested by generating the remote shell
script before packaging.


## v4 naming/readiness update

Default benchmark name is now:

```text
aqsec-ben-machine01
```

Use the next machine as:

```text
aqsec-ben-machine02
```

To create machine02 later, change in `configs/machine.yaml`:

```yaml
machine:
  id: aqsec-ben-machine02
  name: "aqsec-ben-machine02"
```

Initial service wait was reduced:

```yaml
readiness:
  boot_wait_seconds: 10
```

The deployer still waits after that using readiness probes until one forwarded service responds.
