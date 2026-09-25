# AQSEC Benchmark Machine 03 - Venom: 1

This package deploys **Venom: 1** as:

```text
aqsec-ben-machine03
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
Name: Venom: 1
Download: https://download.vulnhub.com/venom/venom.zip
Filename: venom.zip
MD5: E02F7781D4EC766D4F5B22C3DDE59AAB
SHA1: 9811194076C50717A9A31B5A1FD73195D3DA09B2
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
docker build --no-cache -t aqsec-ben-machine03 .
```

## Run

```bash
docker run --rm -it aqsec-ben-machine03
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
