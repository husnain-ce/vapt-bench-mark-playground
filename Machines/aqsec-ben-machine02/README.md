# AQSEC AWS Metasploitable 2 Deployer

Dockerized deployment controller for an **isolated, authorized VAPT lab**.

It provisions an Ubuntu EC2 host, enables AWS nested virtualization, downloads
and verifies the original Metasploitable 2 ZIP, launches it with QEMU/KVM,
preserves guest ports when possible, remaps only host conflicts, and updates
the EC2 security group with the final external ports.

## Important safety behavior

This version deliberately does **not** expose Metasploitable 2 to the whole
Internet. `ALLOWED_CIDR` must be `/24` or narrower; a single researcher IP
(`/32`) is preferred.

Do not use `0.0.0.0/0`.

## AWS host type

`t3.micro` is not a current AWS nested-virtualization-supported instance type.
The default here is:

    m7i-flex.large

The instance type is configurable and the controller checks AWS's
`SupportedFeatures` before launching.

## Build

```bash
docker build -t aqsec-machine-deployer .
```

## Run

Interactive:

```bash
docker run --rm -it aqsec-machine-deployer
```

You will be asked for:

- AWS access key ID
- AWS secret access key
- AWS region
- instance type
- allowed source CIDR, preferably `YOUR.PUBLIC.IP/32`

Or provide environment variables:

```bash
docker run --rm -it \
  -e AWS_ACCESS_KEY_ID="..." \
  -e AWS_SECRET_ACCESS_KEY="..." \
  -e AWS_REGION="us-east-1" \
  -e INSTANCE_TYPE="m7i-flex.large" \
  -e ALLOWED_CIDR="203.0.113.10/32" \
  aqsec-machine-deployer
```

## Port-conflict behavior

If the Ubuntu host already occupies a port, the deployer finds another free
host port. For example, host SSH normally uses TCP/22, so the guest's TCP/22
will typically become 2222 while TCP/21, TCP/23, TCP/80, etc. remain unchanged
when available.

The AWS security group is then updated using the **final external ports**.

## Required AWS permissions

The credentials need permissions for:

- `ec2:Describe*`
- `ec2:RunInstances`
- `ec2:CreateSecurityGroup`
- `ec2:AuthorizeSecurityGroupIngress`
- `ec2:CreateKeyPair`
- `ec2:DeleteKeyPair`
- `ec2:CreateTags`
- `ssm:GetParameter`
- `sts:GetCallerIdentity`

Depending on account policy, `ec2:RunInstances` may also require permissions
for the selected AMI, EBS volume, subnet, network interface, and key pair.

## Notes

- This first version uses the account's **default VPC** and a public subnet that
  auto-assigns a public IPv4 address.
- QEMU uses user-mode networking and `hostfwd`, so the Metasploitable guest is
  NATed behind the Ubuntu EC2 host.
- The ZIP is verified using both the configured MD5 and SHA1 before extraction.
- For a production-quality research platform, add teardown, state persistence,
  cost guards, CloudTrail tagging, private VPC/VPN access, and automated tests.


## Progress output

The deployer now prints all major stages, including:

- AWS credential validation
- AMI and VPC discovery
- security-group creation
- EC2 launch
- EC2 state and health checks
- SSH retry attempts
- occupied-port detection
- QEMU installation
- Metasploitable download / verification / extraction
- final security-group rules

If it appears to stop after creating the instance, look at the `[EC2]` lines.
AWS instance and system health checks can remain `initializing` for a while
even after the instance appears in the EC2 console.

Global `0.0.0.0/0` exposure is intentionally blocked for this deliberately
vulnerable guest. Use the scanner/operator public IP as `/32`.


## Automatic CIDR detection

The deployer no longer asks for `Allowed Cidr`.

It automatically calls AWS's `checkip.amazonaws.com` endpoint from inside
the Docker controller and creates a `/32` rule for that public IPv4 address.

Example:

    [1/13] Detecting deployer public IPv4
        Security-group source: 39.45.120.50/32

An explicit safe override is still possible:

    docker run --rm -it       -e ALLOWED_CIDR="39.45.120.50/32"       aws

Global `0.0.0.0/0` exposure remains blocked because Metasploitable 2 is
deliberately vulnerable.


## Fix: multiline sudo shell scripts

Remote setup scripts are now Base64-encoded by the controller and decoded
directly into `sudo bash` on the EC2 host. This avoids quoting failures caused
by commands such as `$(...)`, `awk '{...}'`, and systemd heredocs.

## Security group behavior

For testing convenience, the deployer now creates one ingress rule that allows
**all IPv4 protocols and ports from the automatically detected operator public
IP `/32`**.

Example:

    ALL traffic from 58.65.220.180/32

This gives the scanner full port access to the benchmark while preventing the
intentionally vulnerable guest from being published to the entire Internet.

## SourceForge checksum update

The current official SourceForge package is verified with SHA-256:

    2ae8788e95273eee87bd379a250d86ec52f286fa7fe84773a3a8f6524085a1ff

The older VulnHub copy uses a different historical MD5/SHA1 pair. Mixing the
current SourceForge download with the older VulnHub hashes causes the checksum
failure seen in earlier builds.

## External forwarding

QEMU host forwarding now binds explicitly to `0.0.0.0` on the Ubuntu EC2 host,
for example:

    hostfwd=tcp:0.0.0.0:80-:80

This makes the forwarded listener reachable through the EC2 network interface.
The AWS security group still limits inbound traffic to the automatically
detected operator/scanner public `/32`.


## Reusable machine configuration

The vulnerable VM is now defined in:

    configs/machine.yaml

To use another vulnerable VM, edit this file:

- `download.url`
- `download.archive_name`
- `download.sha256`
- `disk.format`
- `disk.search_glob`
- `vm.memory_mb`
- `vm.vcpus`
- `ports`

The Python deployment code does not need to be changed for another ZIP-based
QEMU-compatible disk image.

## Manual inbound source IP

The easiest place to set the inbound source manually is:

    configs/deployer.yaml

Change:

    allowed_cidr: "auto"

to, for example:

    allowed_cidr: "58.65.220.180/32"

You can also override it without editing files:

    docker run --rm -it       -e ALLOWED_CIDR="58.65.220.180/32"       aws

The environment variable takes priority over the YAML file.

## Metasploitable 2 port coverage

The machine config now includes the full TCP port set shown in Rapid7's
Metasploitable 2 guide, plus commonly used UDP DNS/RPC/NFS ports.

Some RPC/NFS-related high ports are dynamically assigned by the guest and may
change between boots. Static QEMU `hostfwd` rules cannot discover an unknown
dynamic guest port after boot. For exact runtime discovery of every changing
RPC port, the next architecture should use a TAP/bridge guest network and scan
the guest from the Ubuntu host before installing forwarding rules.
