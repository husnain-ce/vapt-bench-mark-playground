# Metasploitable 2 — Benchmark Target (VulnHub VM)

Rapid7/Metasploit's intentionally vulnerable VM, released 12 Jun 2012.
Unlike Juice Shop/XVWA, this targets vulnerabilities at the **OS and
network-service layer** (outdated daemons, backdoored services, default
credentials) rather than a custom vulnerable web app — it's built as
general target practice for tools like Metasploit and Nmap.

> ⚠️ **This one is widely known to be dangerous if exposed.** Real
> Metasploitable instances left reachable on a public or bridged network
> have been found and exploited in the wild. Only ever run this on a
> Host-Only or NAT network, never Bridged, and never on infrastructure
> reachable from the internet.

## Setup

1. Install [VMware Workstation/Player](https://www.vmware.com/) — this VM
   ships in VMware format (not OVA).
2. Download the zip:
   - `http://sourceforge.net/projects/metasploitable/files/Metasploitable2/metasploitable-linux-2.0.0.zip/download`
   - Mirror: `https://download.vulnhub.com/metasploitable/metasploitable-linux-2.0.0.zip`
3. Verify before extracting:
   ```
   md5sum metasploitable-linux-2.0.0.zip     # expect: 8825F2509A9B9A58EC66BD65EF83167F
   sha1sum metasploitable-linux-2.0.0.zip    # expect: 84133002EF79FC191E726D41265CF5AB0DFAD2F0
   ```
4. Unzip it — contains the VM's `.vmx` and `.vmdk` files.
5. Open it:
   - **VMware:** File > Open, select the `.vmx` file.
   - **VirtualBox:** VirtualBox can use the `.vmdk` directly — create a new
     VM, and when asked for a disk, choose "Use an existing virtual hard
     disk" and point it at the `.vmdk`. No conversion needed.
6. Networking: DHCP is enabled with an auto-assigned IP. Set the network
   adapter to **Host-Only** or **NAT** — see the warning above.
7. Boot the VM, find its IP via `arp-scan` / `netdiscover` on the same
   virtual network, or read it off the VM's own console after login.

## Access notes

- Default login (published by Rapid7 themselves): `msfadmin` / `msfadmin`
- The VulnHub page lists a long history of community walkthroughs if you
  want exploitation guidance beyond setup — not reproduced here.
- Note from the VulnHub listing: their mirror has some edits versus the
  original SourceForge release, mainly for broader VMware compatibility.

## How this fits the benchmark

- No vulnerability mapping table for this one — skipped, same as
  doubletrouble. If you do add one later, OWASP Top 10 likely isn't the
  right categorization for this target (see note above) — consider a
  CVE/service-based checklist instead.
- No `docker-compose.yml` — it's a VM, not a container.
- If you track results against it, tag entries `target: metasploitable2`
  in the shared `../../testcases/` and `../../results/` folders.
