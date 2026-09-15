# Momentum: 2 — Benchmark Target (VulnHub VM)

VulnHub boot2root VM. Difficulty: medium. Released 28 Jun 2021 by AL1ENUM,
part of the "Momentum" series. Keywords listed by the author: curl, bash,
code review. Runs as a self-contained Linux VM, not a container.

## Setup

1. Install [VirtualBox](https://www.virtualbox.org/) — the author notes this
   VM works better on VirtualBox than VMware.
2. Download the OVA:
   `https://download.vulnhub.com/momentum/Momentum2.ova` (698 MB)
3. Verify before importing:
   ```
   md5sum Momentum2.ova     # expect: 5E837FD87D809C499911B1CB1A257CD9
   sha1sum Momentum2.ova    # expect: 17FACC18FE6A6979159C4D0A09CC330602E81E68
   ```
4. In VirtualBox: **File > Import Appliance**, select the `.ova` file.
5. Networking: DHCP is enabled and the IP is auto-assigned. Attach it to a
   **Host-Only** or **NAT** network, not Bridged.
6. Boot the VM, find its IP via `arp-scan` / `netdiscover` on the same
   virtual network, or check VirtualBox's DHCP lease list.

## Access notes

- No published default credentials — boot2root box, access is earned
  progressively as you find vulnerabilities, not via a documented login.
- Medium difficulty, same tier as Chronos: 1. The author's listed keywords
  (curl, bash, code review) suggest this leans more toward scripting/logic
  flaws than the classic network-service angle of Metasploitable 2.

## How this fits the benchmark

- No OWASP Top 10 mapping table — skipped, consistent with the other
  VulnHub VM targets.
- No `docker-compose.yml` — it's a VM, not a container.
- If you track results against it, tag entries `target: momentum-2` in the
  shared `../../testcases/` and `../../results/` folders.
