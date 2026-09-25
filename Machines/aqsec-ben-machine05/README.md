# AQSEC Benchmark Machine 05 - NoobBox: 1

This package deploys **NoobBox: 1** as:

```text
aqsec-ben-machine05
```

Default AWS instance type:

```text
c8i.large
```

Root EBS volume:

```text
35 GiB
```

## VulnHub details used

```text
Name: NoobBox: 1
Download: https://download.vulnhub.com/noobbox/NoobBox.zip
Filename: NoobBox.zip
MD5: DA2987BD8B1F07CF20F1041D327C13BF
SHA1: A92FD485BDF39A18FED4EFE158C8B15084845B6B
Format: ZIP containing VirtualBox OVA
Networking: DHCP enabled
```

## Behavior

- ZIP with nested OVA support.
- Direct OVF/VMDK fallback if no OVA is found.
- Converts VMDK to QCOW2 before boot.
- Uses KVM if `/dev/kvm` exists; otherwise TCG fallback.
- Initial readiness wait: 10 seconds.
- Ubuntu SSH stays on host port 22.
- Guest SSH 22 remaps to host 2222.
- Guest HTTP 80 maps to host 80.
- Default EC2 instance type: c8i.large.
- Root volume size: 35 GiB.

## Build

```bash
docker build --no-cache -t aqsec-ben-machine05 .
```

## Run

```bash
docker run --rm -it aqsec-ben-machine05
```

## Expected mapping

```text
22/tcp guest -> 2222/tcp host
80/tcp guest -> 80/tcp host
```

## Scan

```bash
nmap -Pn -sV -p 80,2222 PUBLIC_IP
```
