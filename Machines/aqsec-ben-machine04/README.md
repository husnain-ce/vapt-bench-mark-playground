# AQSEC Benchmark Machine 04 - Beelzebub: 1

This package deploys **Beelzebub: 1** as:

```text
aqsec-ben-machine04
```

Default AWS instance type:

```text
c8i.large
```

Root EBS volume is set to **35 GiB** because the ZIP is about 4.1 GB and extraction + QCOW2 conversion need extra working space.

## VulnHub details used

```text
Name: Beelzebub: 1
Download: https://download.vulnhub.com/beelzebub/Beelzebub.zip
Filename: Beelzebub.zip
MD5: BAC51D7645855EB6A45F90F5273A34F2
SHA1: C033AEB91D81E08640EDB0B163CBDC27AE75D98E
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

## Build

```bash
docker build --no-cache -t aqsec-ben-machine04 .
```

## Run

```bash
docker run --rm -it aqsec-ben-machine04
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


## v2 storage update

Root EBS volume changed to **35 GiB** as requested.
