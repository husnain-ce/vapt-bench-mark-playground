# Metasploitable 3 — KVM path (best-effort) vs the working container

You asked for full parity including a KVM Metasploitable 3. Here is the honest
state and how to pursue the real VM if your target host can host it.

## TL;DR

- **The guaranteed-working MS3 in this kit is a container** — `vm/ms3-lite`,
  deployed by `bin/deploy-net.sh` at `172.30.0.12`. It reproduces the classic
  MS3-ub1404 vulnerable surface (ProFTPd 1.3.5 mod_copy CVE-2015-3306, weak SSH
  creds, PHP command injection, SQLi). Use this unless you specifically need a
  full VM.
- **The KVM path is scaffolding only.** The original host's
  `ms3-ub1404.box` was a *truncated, VirtualBox-format* download (unusable vmdk,
  ~1.7 GB) with no packer/vagrant to rebuild it, so a real KVM MS3 was never
  stood up. That broken 1.7 GB box is deliberately **not** shipped in this kit.
  To get a real VM you must supply a valid box on the target (steps below).

## What ships for the KVM path

- `vm/kvm/ms3-range-net.xml` — a libvirt NAT network (`ms3-range`,
  `172.28.128.0/24`, static lease `ms3 → 172.28.128.30`).

## Standing up a real KVM Metasploitable 3 (on a capable host)

Requirements: nested virtualization, `libvirt` + `qemu-kvm`, `vagrant` with the
`vagrant-libvirt` plugin, and **≥ 4 GB RAM free for the guest**.

```bash
# 1. host packages (Debian/Ubuntu)
sudo apt-get install -y qemu-kvm libvirt-daemon-system virtinst vagrant
vagrant plugin install vagrant-libvirt

# 2. define the isolated range network
sudo virsh net-define vm/kvm/ms3-range-net.xml
sudo virsh net-start ms3-range
sudo virsh net-autostart ms3-range

# 3. get a VALID Metasploitable 3 box for the libvirt provider
#    (do NOT reuse the truncated virtualbox box)
vagrant box add rapid7/metasploitable3-ub1404 --provider libvirt
#    …or build from source with packer (rapid7/metasploitable3), then
#    `vagrant package` / `vagrant mutate` to a libvirt box.

# 4. bring the guest up on the ms3-range network, then confirm services:
#    ProFTPd 21, SSH 22, Apache 80, plus the Windows-side services if you use
#    the win2k8 variant. Point ms3.range.example.com at the guest's lease IP.
```

If your target VM cannot nest virtualization (most cloud VMs without nested-virt
enabled), stay on the **MS3-lite container** — it exercises the same headline CVE
and credential/injection surface a scanner needs to find, at ~90 MB instead of a
multi-GB guest.

## Reconciling the two in the range

- The container binds `ms3.range.example.com → 172.30.0.12` (via `/etc/hosts`).
- A KVM guest instead lives at its `ms3-range` lease (e.g. `172.28.128.30`). If you
  run the real VM, repoint the `ms3.range.example.com` line in
  `hosts/aqira-range.hosts` to the guest IP and re-run `bin/install-hosts.sh`, and
  stop the container (`docker compose -f compose/netlab-ms3.yml down`) so only one
  MS3 answers.
