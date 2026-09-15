# hacksudo: 1.0.1 — Benchmark Target (VulnHub VM)

VulnHub boot2root VM. Released 4 Apr 2021 by Vishal Waghmare, part of the
"hacksudo" series (v1.0.1, up from v1.0.0 on 2021-02-22). No difficulty or
description published for this entry. Runs as a self-contained Linux VM,
not a container.

## Setup

1. Install [VirtualBox](https://www.virtualbox.org/) — the author notes this
   VM works better on VirtualBox than VMware.
2. Download the zip (this one ships zipped, not as a bare `.ova` like the
   other targets — expect a longer download at 3.7 GB):
   `https://download.vulnhub.com/hacksudo/hacksudo1.1.zip`
3. Verify before extracting:
   ```
   md5sum hacksudo1.1.zip     # expect: 359379AF7615BD336A3D32B4969746BF
   sha1sum hacksudo1.1.zip    # expect: 2ABDEC98C00B7C51C037BAFEF8F89A6FC229AA20
   ```
4. Unzip it to get the `.ova` file inside.
5. In VirtualBox: **File > Import Appliance**, select the extracted `.ova`.
6. Networking: DHCP is enabled and the IP is auto-assigned. Attach it to a
   **Host-Only** or **NAT** network, not Bridged.
7. Boot the VM, find its IP via `arp-scan` / `netdiscover` on the same
   virtual network, or check VirtualBox's DHCP lease list.

## Access notes

- No published default credentials — boot2root box, access is earned
  progressively as you find vulnerabilities, not via a documented login.
- No difficulty rating was published for this release — worth noting in
  your own tracking once you've tried it, so future-you (or your teammate)
  knows roughly where it sits relative to the others.
- Minor naming note: the VM entry is called "1.0.1" but the download file
  is named `hacksudo1.1.zip` — this appears to just be a filename
  convention, not a version mismatch, but the checksums above confirm
  you've got the right file either way.

## How this fits the benchmark

- No OWASP Top 10 mapping table — skipped, consistent with the other
  VulnHub VM targets.
- No `docker-compose.yml` — it's a VM, not a container.
- If you track results against it, tag entries `target: hacksudo-101` in
  the shared `../../testcases/` and `../../results/` folders.