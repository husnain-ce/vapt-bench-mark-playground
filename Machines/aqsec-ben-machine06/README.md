# AQSEC Benchmark Machine 06 - FinitHicDeo: 1

This package deploys **FinitHicDeo: 1** as:

```text
aqsec-ben-machine06
```

Settings:

```text
Instance type: c8i.large
Root storage: 35 GiB
Initial boot wait: 10 seconds
```

## VulnHub details used

```text
Name: FinitHicDeo: 1
Download: https://download.vulnhub.com/fhd/FHD_CTF.zip
Filename: FHD_CTF.zip
MD5: D2BE74CE12849C1F14E6D6F0D3D5407B
SHA1: 307F013354A5459E9D69B419A84505E05A30F593
Format: ZIP containing VirtualBox OVA
Networking: DHCP enabled
```

## Expected mapping

```text
22/tcp guest   -> 2222/tcp host
80/tcp guest   -> 80/tcp host
8080/tcp guest -> 8080/tcp host
```

## Build

```bash
docker build --no-cache -t aqsec-ben-machine06 .
```

## Run

```bash
docker run --rm -it aqsec-ben-machine06
```

## Scan

```bash
nmap -Pn -sV -p 80,8080,2222 PUBLIC_IP
```
