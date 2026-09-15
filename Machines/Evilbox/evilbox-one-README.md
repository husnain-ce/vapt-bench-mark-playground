# EvilBox: One — Benchmark Target (VulnHub VM)

VulnHub boot2root VM. Difficulty: easy. Released 16 Aug 2021 by Mowree, part
of the "EvilBox" series. Like doubletrouble, this runs as a self-contained
Linux VM, not a container.

## Setup

1. Install [VirtualBox](https://www.virtualbox.org/) — the author notes this
   VM works better on VirtualBox than VMware.
2. Download the OVA:
   `https://download.vulnhub.com/evilbox/EvilBox---One.ova` (712 MB)
3. Verify before importing:
   ```
   md5sum EvilBox---One.ova     # expect: C3A65197B891713731E6BB791D7AD259
   sha1sum EvilBox---One.ova    # expect: EE44F1720A5D80B389AAA8207FE99F8C8C48C509
   ```
4. In VirtualBox: **File > Import Appliance**, select the `.ova` file.
5. Networking: DHCP is enabled and the IP is auto-assigned. Attach it to a
   **Host-Only** or **NAT** network, not Bridged.
6. Boot the VM, find its IP via `arp-scan` / `netdiscover` on the same
   virtual network, or check VirtualBox's DHCP lease list.

## Access notes

- No published default credentials — boot2root box, access is earned
  progressively as you find vulnerabilities, not via a documented login.

## How this fits the benchmark

- No OWASP Top 10 mapping table — skipped, same as doubletrouble and
  Metasploitable 2.
- No `docker-compose.yml` — it's a VM, not a container.
- If you track results against it, tag entries `target: evilbox-one` in the
  shared `../../testcases/` and `../../results/` folders.
