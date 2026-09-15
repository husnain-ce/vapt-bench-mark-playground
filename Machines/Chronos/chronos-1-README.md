# Chronos: 1 — Benchmark Target (VulnHub VM)

VulnHub boot2root VM. Difficulty: medium. Released 9 Aug 2021 by AL1ENUM,
part of the "Chronos" series. Runs as a self-contained Linux VM, not a
container.

## Setup

1. Install [VirtualBox](https://www.virtualbox.org/) — the author notes this
   VM works better on VirtualBox than VMware.
2. Download the OVA:
   `https://download.vulnhub.com/chronos/Chronos.ova` (1.7 GB)
3. Verify before importing:
   ```
   md5sum Chronos.ova     # expect: 30DAD56028D2AAAD047391E76BE64F9C
   sha1sum Chronos.ova    # expect: 73392A63F0C1662793907982CC1E1CB745703DF3
   ```
4. In VirtualBox: **File > Import Appliance**, select the `.ova` file.
5. Networking: DHCP is enabled and the IP is auto-assigned. Attach it to a
   **Host-Only** or **NAT** network, not Bridged.
6. Boot the VM, find its IP via `arp-scan` / `netdiscover` on the same
   virtual network, or check VirtualBox's DHCP lease list.

## Access notes

- No published default credentials — boot2root box, access is earned
  progressively as you find vulnerabilities, not via a documented login.
- Medium difficulty — a step up from doubletrouble and EvilBox: One, worth
  attempting after those if you're sequencing targets by difficulty.

## How this fits the benchmark

- No OWASP Top 10 mapping table — skipped, consistent with the other
  VulnHub VM targets.
- No `docker-compose.yml` — it's a VM, not a container.
- If you track results against it, tag entries `target: chronos-1` in the
  shared `../../testcases/` and `../../results/` folders.
