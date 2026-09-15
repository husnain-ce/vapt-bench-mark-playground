# Benchmrks

A collection of vulnerable target benchmarks organized by domain, used for practicing and evaluating security testing workflows (manual testing, automated scanning, tool development, etc.).

## Overview

This repository groups **130+ benchmark target directories** across 8 domains. Each subfolder represents an isolated target/lab (`*-ben1`, `*-ben2`, ...) that can be spun up and tested against independently.

```
Benchmrks/
├── android/    # Android application security targets
├── API/        # API security targets (REST/GraphQL, auth, injection, etc.)
├── Cloud/      # Cloud misconfiguration & cloud-native attack surface targets
├── Machines/   # Named vulnerable VMs (VulnHub/HTB-style boot2root machines)
├── mobile/     # General mobile app security targets
├── Web/        # Web application security targets
└── ios/        # iOS application security targets
```

## Purpose

These benchmarks are intended strictly for:

- Practicing and validating security testing methodology in a controlled/lab environment
- Benchmarking automated scanners or custom tooling against known-vulnerable targets
- Training/education (e.g. OSCP-style practice, internal team drills)

## Usage

1. Choose a target directory relevant to the domain you want to test (e.g. `Web/aq-web-ben1`).
2. Follow the setup instructions inside that target's directory (add a `setup.md`/`docker-compose.yml` per target as you build them out).
3. Run your tool/scanner/manual test against the deployed target.


## Disclaimer

These targets are intentionally vulnerable and must only be run in isolated, non-production environments (local VM, isolated network segment, or containerized sandbox). Do not expose these targets to the public internet.

## Contributing

When adding a new benchmark:
1. Create a folder following the existing naming convention for that domain.
2. Include a short `README.md` inside describing the vulnerability class being tested.
3. Update the table above with the new count.
