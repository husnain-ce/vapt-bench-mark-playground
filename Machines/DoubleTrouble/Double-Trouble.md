# doubletrouble: 1 — Benchmark Target (VulnHub VM)

VulnHub boot2root VM. Difficulty: easy. Released 11 Sep 2021 by tasiyanci,
part of the "doubletrouble" series. Objective is to find flags — this runs
as a self-contained Linux VM, not a container like the other targets.

## Setup

1. Install [VirtualBox](https://www.virtualbox.org/) — the author notes this
   VM works better on VirtualBox than VMware.
2. Download the OVA:
   `https://download.vulnhub.com/doubletrouble/doubletrouble.ova` (979 MB)
3. Verify the download before importing (large file from a third-party
   mirror, worth checking):
   ```
   md5sum doubletrouble.ova     # expect: F56544B46DC149ECA71F948E9F10772F
   sha1sum doubletrouble.ova    # expect: B17C92DF8F73E391AFC90EA583243566DF3381EC
   ```
4. In VirtualBox: **File > Import Appliance**, select the `.ova` file.
5. Networking: DHCP is enabled and the IP is auto-assigned. Attach the VM to
   a **Host-Only** or **NAT** network, not Bridged, so it stays off your
   real LAN.
6. Boot the VM. Since the IP is assigned automatically, find it from your
   host with `arp-scan` / `netdiscover` on the same virtual network, or
   check VirtualBox's DHCP lease list.

## Access notes

- No published default credentials — this is a boot2root box, so access is
  earned progressively as you find flags/vulnerabilities, not via a
  documented login.
- Nested VT-x/AMD-V is enabled on this VM — if you're running it inside
  another hypervisor yourself, your host needs to support nested
  virtualization.
- The author lists an email contact on the VulnHub page for VM-specific
  issues (not for hints on solving it).

## How this fits the benchmark

- No OWASP Top 10 mapping table for this one — skipped for now. Add one
  later if you decide to fold it into the formal comparison; until then
  treat it as a free-form practice target outside the main matrix.
- No `docker-compose.yml` in this folder — it's a VM, not a container.
- If you do end up testing against it, results/test cases still go in the
  shared `../../testcases/` and `../../results/` folders, tagged
  `target: doubletrouble`, same as the other targets.

